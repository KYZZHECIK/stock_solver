from datetime import datetime, timedelta
from pathlib import Path

from typing import Generator, Dict, List, Any

from joblib import Memory # type: ignore
import pandas as pd
from tqdm import tqdm
import json

import stock_solver.dataset.apis.alpha_vantage as AV

TICKERS_LIMIT = 500
TIME_STEP = timedelta(weeks=1)
NEWS_LIMIT_PER_REQUEST = 1000

memory = Memory(".alpha_vantage_cache", verbose=0)


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
    result = AV.TimeSeriesResult.parse(response.json())
    raw = {ts_str: ohlcv.model_dump() for ts_str, ohlcv in result.time_series.items()}
    if not raw:
        print(f"Daily Time Series for {symbol} are missing, skipping.")        
        raise AV.APIError()
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
def fetch_insider_transactions(symbol: str) -> pd.DataFrame:
    response = AV.InsiderTransactionsRequest(symbol=symbol).query()
    result = AV.InsiderTransactionsResult().parse(response.json())

    # TODO: Not entirely sure if insider transaction endpoint returns the amount of shares
    # acquired/disposed, so check when you have internet, keep a binary feature for now
    raw: Dict[str, int] = {}
    for transaction in result.data:
        raw[transaction.transaction_date] = 1 if transaction.acquisition_or_disposal == 'A' else 0
    df = pd.DataFrame.from_dict(raw, orient="index")
    df.index = pd.to_datetime(df.index, errors="coerce")
    df.index.name = "date"
    df = df.sort_index()
    return df


@memory.cache # type: ignore
def fetch_news_sentiment(symbol: str, time_from: datetime, time_to: datetime) -> pd.DataFrame:
    raw: Dict[str, Any] = {}
    columns = ["relevance_score", "ticker_sentiment_score"]
    for start, end in tqdm(
        time_iterator(time_from, time_to, TIME_STEP),
        total=time_iterator_len(time_from, time_to, TIME_STEP),
        desc=f"{symbol} news collection"
        ):
        response = AV.NewsRequest(
            tickers=[symbol],
            time_from=start,
            time_to=end,
            limit=NEWS_LIMIT_PER_REQUEST
        ).query()
        result = AV.NewsResult.parse(response.json())

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


@memory.cache # type: ignore
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


@memory.cache # type: ignore
def build_features_for_ticker(symbol:str) -> pd.DataFrame:
    time_series_df = fetch_daily_OHLCV(symbol)
    min_date = time_series_df.index.min()

    news_df = fetch_news_sentiment(symbol, min_date, datetime.today())
    news_df = aggregate_news_sentiment(news_df)
    news_cols = news_df.columns

    # We get NaNs when performing the join on missing entries for news
    time_series_df = time_series_df.join(news_df, how="left") 
    time_series_df[news_cols] = time_series_df[news_cols].fillna(0.0)
    
    # TODO: add the insider transaction df here 
    return time_series_df


@memory.cache # type: ignore
def populate_dataset(symbols: List[str]) -> Dict[str, pd.DataFrame]:
    return {symbol: build_features_for_ticker(symbol) for symbol in tqdm(symbols, total=len(symbols), desc=f"Processing the tickers.")}


def save_dataset(data: Dict[str, pd.DataFrame], root: str = ".alpha_vantage_cache", folder: str = "dataset"):
    path = Path(root) / folder
    path.mkdir(parents=True, exist_ok=True)

    manifest: Dict[str, Any] = {
        "version": "1",
        "created_at": datetime.now().strftime("%d/%m/%Y, %H:%M:%S"),
        "tickers": []
    }

    for ticker, df in data.items():
        out_path = path / f"{ticker}.parquet"
        df.reset_index().to_parquet(
            out_path,
            engine="pyarrow",
            compression="zstd"
        )
        manifest["tickers"].append({"ticker": ticker, "file": f"{ticker}.parquet"})
    (path / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        

def load_dataset(root: str = ".alpha_vantage_cache", folder: str = "dataset") -> Dict[str, pd.DataFrame]:
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


if __name__ == '__main__':
    tickers = [
    "AAPL",
    "MSFT",
    # "AMZN",
    # "GOOG",
    # "GOOGL",
    # "META",
    ]
    # memory.clear(warn=False)
    save_dataset(populate_dataset(tickers))

