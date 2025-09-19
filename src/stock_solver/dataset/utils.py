import os
from typing import NamedTuple

from dotenv import load_dotenv
import src.stock_solver.dataset.apis.alpha_vantage as AV
import pandas as pd

from contextlib import contextmanager
import time

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


def fetch_daily_OHLCV(symbol: str) -> pd.DataFrame:
    with tmark("request"):
        response = AV.TimeSeriesDailyRequest(symbol=symbol).query()
    with tmark("parsing"):
        result = AV.TimeSeriesResult.parse(response.json())

    with tmark("build_dataframe"):
        raw = {ts_str: ohlcv.model_dump() for ts_str, ohlcv in result.time_series.items()}
        if not raw:
            print(f"Daily Time Series for {symbol} are missing, skipping.")        
            raise AV.APIError()
        
        df = pd.DataFrame.from_dict(raw, orient="index")

    with tmark("indexing"):
        idx = pd.to_datetime(df.index, errors="coerce")
        df.index = idx
        df.index.name = "date"
        df = df.sort_index()

    for col in ("open", "high", "low", "close", "adjusted_close"):
        df[col] = pd.to_numeric(df[col], errors='coerce').astype('float32')
    df["volume"] = pd.to_numeric(df["volume"], errors='coerce').astype('int64')

    # print(df.info())
    # print(df)
    return df


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

    
    print(f"avg #rows = {sum(len(fetch_daily_OHLCV(ticker).index) for ticker in tickers) / len(tickers)}")
    # for ticker in tickers:
    #     print(f'start day for {ticker} is {min(fetch_daily_OHLCV(ticker).index)}') 
