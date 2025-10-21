from datetime import datetime, timedelta
import time
from pathlib import Path

from typing import Generator, Dict, List, Any

from joblib import Memory # type: ignore
import pandas as pd
from tqdm import tqdm
import json

from ..utils import get_logger
from .alpaca import get_assets
from . import alpha_vantage as AV

TIME_STEP = timedelta(days=30)
NEWS_LIMIT_PER_REQUEST = 500
MIN_MARKET_CAPITALIZATION = 1_000_000_000

MAX_RETRIES = 3
RETRY_WAIT = 60 # number of seconds to wait on api error before retrying

memory = Memory(".alpha_vantage_cache", verbose=0)
logger = get_logger()


def time_iterator(
    start: datetime, end: datetime, step: timedelta
) -> Generator[tuple[datetime, datetime], None, None]:
    cur = start
    next = start + step
    while next < end:
        yield cur, next
        cur += step
        next += step


def time_iterator_len(start: datetime, end: datetime, step: timedelta) -> int:
    count = 0
    next = start + step
    while next < end:
        count += 1
        next += step
    return count


@memory.cache # type: ignore
def fetch_daily_OHLCV(symbol: str) -> pd.DataFrame:
    response = AV.TimeSeriesDailyRequest(symbol=symbol, outputsize="full").query()
    result = AV.TimeSeriesResult.model_validate(response.json())
    raw = {ts_str: ohlcv.model_dump() for ts_str, ohlcv in result.time_series.items()}
    df = pd.DataFrame.from_dict(raw, orient="index")
    idx = pd.to_datetime(df.index, errors="coerce")
    df.index = idx
    df.index.name = "date"
    df = df.sort_index()
    for col in ("open", "high", "low", "close", "volume", "adjusted_close"):
        df[col] = pd.to_numeric(df[col], errors='coerce').astype('float32')
    df["volume"] = pd.to_numeric(df["volume"], errors='coerce').astype('int64')
    return df


@memory.cache # type: ignore
def fetch_overview(symbol: str):
    return AV.OverviewRequest(symbol=symbol).query().json()


@memory.cache # type: ignore
def fetch_news_sentiment(symbol: str, time_from: datetime, time_to: datetime) -> pd.DataFrame:
    raw: Dict[str, Any] = {}
    columns = ["relevance_score", "ticker_sentiment_score"]
    for start, end in tqdm(
        time_iterator(time_from, time_to, TIME_STEP),
        total=time_iterator_len(time_from, time_to, TIME_STEP),
        desc=f"{symbol} news collection",
        leave=False
        ):
        response = AV.NewsRequest(
            tickers=[symbol],
            time_from=start,
            time_to=end,
            limit=NEWS_LIMIT_PER_REQUEST
        ).query()
        try:
            result = AV.NewsResult.model_validate(response.json())
        except:
            continue    

        # Each item in the feed has a list of tickers that are mentioned in the article,
        # this way we are extracting the ticker that we need
        for item in result.feed:
            ticker_match = next((x for x in item.ticker_sentiment if x.ticker == symbol), None)
            if ticker_match is None:
                continue
            raw[item.time_published] = {
                "relevance_score": ticker_match.relevance_score,
                "ticker_sentiment_score": ticker_match.ticker_sentiment_score
            }
    if not raw:
        return pd.DataFrame(columns=columns)
    df = pd.DataFrame.from_dict(raw, orient="index")
    for col in columns:
        df[col] = pd.to_numeric(df[col], errors="coerce").astype('float32')
    return df


def aggregate_news_sentiment(raw: pd.DataFrame) -> pd.DataFrame:
    idx = pd.to_datetime(raw.index, utc=True, errors='coerce').tz_convert("America/New_York")
    group = idx.normalize()
    
    rel = raw["relevance_score"]
    sent = raw["ticker_sentiment_score"].clip(-1.0, 1.0)
    rsum = rel.groupby(group).sum().rename("relavance_sum")
    wsum = (rel * sent).groupby(group).sum().rename("news_sentiment_wsum")
    wmean = wsum.div(rsum).where(rsum > 0, 0.0).astype("float32")
    wmean = ((wmean + 1.0) / 2.0).rename("news_sentiment_wmean")
    count = pd.Series(1, index=raw.index).groupby(group).sum().rename("news_count")
    
    out = pd.concat([wmean, count], axis = 1).sort_index()
    out.index = out.index.tz_localize(None)
    out.index.name = "date" 
    return out


def build_features_for_ticker(symbol:str) -> pd.DataFrame:
    time_series_df = fetch_daily_OHLCV(symbol)
    min_date = time_series_df.index.min()

    news_df = fetch_news_sentiment(symbol, min_date, datetime.today())
    news_df = aggregate_news_sentiment(news_df)
    news_cols = news_df.columns

    # We get NaNs when performing the join on missing entries for news
    time_series_df = time_series_df.join(news_df, how="left") 
    time_series_df[news_cols] = time_series_df[news_cols].fillna(0.0)
    return time_series_df


def save_data(
    symbols: List[str],
    path: Path = Path(".alpha_vantage_cache", "dataset"),
    overwrite: bool = False,
):
    path.mkdir(parents=True, exist_ok=True)
    logger.info(f"Started to process len(symbols) tickers")
    for symbol in tqdm(symbols, total=len(symbols), desc="Saving features for tickers"):
        attempt = 0
        while True:
            try:
                out_path = save_ticker(symbol, path=path, overwrite=overwrite)
                update_manifest_entry(symbol, out_path.name, path / "manifest.json")
                logger.info(f"Processed and saved {symbol}")
                break
            except AV.APIError as api_error:
                attempt += 1
                logger.error(f"{symbol} | {api_error}")
                if attempt < MAX_RETRIES:
                    time.sleep(RETRY_WAIT)
                    continue
                else: 
                    logger.critical(f"{symbol} | Maximum number of retries was achieved.")
                    break
            except Exception as error:
                logger.critical(f"{symbol} | {error}")
                break
    
def save_ticker(symbol: str, path: Path, overwrite: bool = False) -> Path:
    out_path = path / f"{symbol}.parquet"
    
    if out_path.exists() and not overwrite:
        return out_path
    
    df = build_features_for_ticker(symbol)
    tmp = out_path.with_suffix(out_path.suffix + ".tmp")
    try:
        df.reset_index().to_parquet(tmp, engine="pyarrow", compression="zstd")
        tmp.replace(out_path)
    finally:
        try:
            if tmp.exists() and not out_path.exists():
                tmp.unlink()
        except:
            pass
    return out_path
    
def update_manifest_entry(ticker: str, file_name: str, manifest_path: Path):
    if manifest_path.exists():
        manifest: Dict[str, Any] = json.loads(manifest_path.read_text(encoding="utf-8"))
    else:
        manifest = {"version": 1, "created_at": datetime.now().strftime("%d/%m/%Y, %H:%M:%S"), "tickers": []}
    
    manifest["tickers"] = [t for t in manifest["tickers"] if t["ticker"] != ticker]
    manifest["tickers"].append({"ticker": ticker, "file": file_name})
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")



def load_data(root: str = ".alpha_vantage_cache", folder: str = "dataset") -> Dict[str, pd.DataFrame]:
    path = Path(root) / folder
    manifest_path = path / "manifest.json"

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    data: Dict[str, pd.DataFrame] = {}
    for item in manifest["tickers"]:
        ticker = item["ticker"]
        file = path / item["file"]
        df = pd.read_parquet(file, engine='pyarrow')
        df["date"] = pd.to_datetime(df["date"], utc=False, errors='raise')
        data[ticker] = df
    return data


@memory.cache
def filter_tickers(all_tickers: List[str]) -> List[str]:
    tickers: List[str] = []
    for ticker in tqdm(all_tickers, total=len(all_tickers), desc='Choosing Tickers'):
        response = AV.OverviewRequest(symbol=ticker).query()
        try:
            _ = AV.OverviewResult.model_validate(response.json())
            tickers.append(ticker)
        except:
            continue
    return tickers


if __name__ == '__main__':
    ...
    memory.clear(warn=False)
    with open('tickers', 'r', encoding='utf-8') as file:
        tickers = file.readlines()
    tickers = [ticker.strip() for ticker in tickers]
    save_data(tickers, overwrite=True)