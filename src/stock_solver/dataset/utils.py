import os
from typing import NamedTuple
from dotenv import load_dotenv

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