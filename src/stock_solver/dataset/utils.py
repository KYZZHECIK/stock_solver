import os
from typing import NamedTuple
from datetime import datetime

from dotenv import load_dotenv
import src.stock_solver.dataset.apis.alpha_vantage as AV
import pandas as pd
import numpy as np

from contextlib import contextmanager
import time

from joblib import Memory # type: ignore

memory = Memory(".alpha_vantage_cache", verbose=0)

@contextmanager
def tmark(label: str):
    t0 = time.perf_counter()
    yield
    dt = time.perf_counter() - t0
    print(f"time [{label}]: {dt:.4f}s")


class API_KEYS(NamedTuple):
    alpaca_api: str
    alpaca_secret: str
    alpha_vantage_api: str


def api_keys() -> API_KEYS:
    load_dotenv()

    alpaca_api_key = os.environ["ALPACA_API_KEY"]
    alpaca_secret_key = os.environ["ALPACA_SECRET_KEY"]
    alpha_vantage_api_key = os.environ["ALPHA_VANTAGE_API_KEY"]

    return API_KEYS(
        alpaca_api=alpaca_api_key,
        alpaca_secret=alpaca_secret_key,
        alpha_vantage_api=alpha_vantage_api_key,
    )


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
