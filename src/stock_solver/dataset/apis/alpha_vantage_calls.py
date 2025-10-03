from datetime import date, datetime, timedelta
from typing import Generator, Dict

from joblib import Memory # type: ignore
from tqdm import tqdm
import pandas as pd
from src.stock_solver.dataset.apis.alpaca import get_assets

import stock_solver.dataset.apis.alpha_vantage as AV

TICKERS_LIMIT = 500
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
    response = AV.TimeSeriesDailyRequest(symbol=symbol).query()
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

    for col in ("open", "high", "low", "close", "adjusted_close"):
        df[col] = pd.to_numeric(df[col], errors='coerce').astype('float32')
    df["volume"] = pd.to_numeric(df["volume"], errors='coerce').astype('int64')

    return df


# @memory.cache # type: ignore
def fetch_news_sentiment(symbol: str, time_from: datetime, time_to: datetime) -> pd.DataFrame:
    # FIXME: News are not returned fully. No nes are for the latest year, increasing limit to 10_000 returns less news somehoww
    response = AV.NewsRequest(tickers=[symbol], time_from=time_from, time_to=time_to, limit=1000).query()
    result = AV.NewsResult.parse(response.json())

    raw = {}
    for item in result.feed:
        ticker_match = next((x for x in item.ticker_sentiment if x.ticker == symbol))
        raw[item.time_published] = ticker_match.model_dump()
        
    df = pd.DataFrame.from_dict(raw, orient="index")
    df = df.drop(columns=["ticker_sentiment_label"])
    for col in ("relevance_score", "ticker_sentiment_score"):
        df[col] = pd.to_numeric(df[col], errors="coerce").astype('float32')
        
    return df

# FIXME:
def aggregate_news_sentiment(raw: pd.DataFrame) -> pd.DataFrame:
    dates = pd.to_datetime(raw.index.str[:8], format="%Y%m%d", errors="coerce") 

    work = pd.DataFrame({
        "date": dates,
        "relevance_score": raw["relevance_score"],
        "ticker_sentiment_score": raw["ticker_sentiment_score"]
    })        

    work["wx"] = work["relevance_score"] * work["ticker_sentiment_score"]
    g = work.groupby("date", sort=True)
    rel_sum = g["relevance_score"].sum()
    wsum = g["wx"].sum()
    count = g.size()

    out = pd.DataFrame({
        "news_count": count.astype("int32"),
        "news_rel_sum": rel_sum.astype("float32"),
        "news_sent_wsum": wsum.astype("float32"),
    })

    out.index.name = "date"
    return out.sort_index()
        

        
if __name__ == '__main__':
    tickers = [
    "AAPL",
    "MSFT",
    "AMZN",
    "GOOG",
    "GOOGL",
    "META",
    "NVDA",
    "TSLA",
    "NFLX",
    "AMD",
    "JPM"
    ]

    min_date = datetime(1999, 11, 1)
    print(aggregate_news_sentiment(fetch_news_sentiment(symbol=tickers[0], time_from=min_date, time_to=datetime.now())))