from datetime import datetime, timedelta
from typing import Generator

from joblib import Memory
import requests
from requests import Response, Request, Session
from tqdm import tqdm

from pydantic import BaseModel

from src.stock_solver.dataset.utils import api_keys
from src.stock_solver.dataset.apis.alpaca import get_assets

api_key = api_keys().alpha_vantage_api
TICKERS_LIMIT = 500
memory = Memory(".alpha_vantage_cache", verbose=0)


class AlphaVantageRequest(BaseModel):
    function: str
    apikey: str = api_key

    def params(self) -> dict[str, str]:
        return {
            "function": self.function,
            "apikey": self.apikey,
        }

    def query(self) -> Response:
        base_url = "https://www.alphavantage.co/query"
        params = self.params()
        req = Request("GET", base_url, params=params)
        prepped = Session().prepare_request(req)
        # print(prepped.url)
        response = requests.get(base_url, params=params)
        if not response.ok:
            raise ValueError(f"Error fetching data from Alpha Vantage: {response.reason}")
        return response


class AlphaVantageTickersRequest(AlphaVantageRequest):
    tickers: list[str]

    def params(self) -> dict[str, str]:
        params = super().params()
        ticker_sep = "," if len(self.tickers) > 1 else ""
        params["tickers"] = ticker_sep.join(self.tickers)
        return params


class AlphaVantageSymbolRequest(AlphaVantageRequest):
    symbol: str

    def params(self) -> dict[str, str]:
        params = super().params()
        params["symbol"] = self.symbol
        return params


class AlphaVantageNewsRequest(AlphaVantageTickersRequest):
    function: str = "NEWS_SENTIMENT"
    time_from: datetime
    time_to: datetime
    limit: int

    def params(self) -> dict[str, str]:
        params = super().params()
        # convert to YYYYMMDDTHHMM
        time_str = "%Y%m%dT%H%M"
        params["time_from"] = self.time_from.strftime(time_str)
        params["time_to"] = self.time_to.strftime(time_str)
        params["limit"] = str(self.limit)
        params["sort"] = "EARLIEST"
        return params


class AlphaVantageOverviewRequest(AlphaVantageSymbolRequest):
    function: str = "OVERVIEW"


class AlphaVantageNewsTickerSentiment(BaseModel):
    ticker: str


class AlphaVantageNewsFeedItem(BaseModel):
    ticker_sentiment: list[AlphaVantageNewsTickerSentiment]


class AlphaVantageNewsResult(BaseModel):
    items: int
    sentiment_score_definition: str
    relevance_score_definition: str
    feed: list[AlphaVantageNewsFeedItem]


@memory.cache
def collect_overview():
    assets = get_assets()
    symbols = [a.symbol for a in assets]
    data = {}
    for s in tqdm(symbols):
        request = AlphaVantageOverviewRequest(symbol=s)
        try:
            result = request.query()
        except ValueError:
            print(f"Failed to fetch overview for {s}, skipping.")
            continue
        if j := result.json():
            data[s] = j
    return data


def time_iterator(
    start: datetime, end: datetime, step: timedelta
) -> Generator[tuple[datetime, datetime]]:
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


# TODO: this doesn't work yet
@memory.cache
def collect_news(tickers: list[str]) -> list[AlphaVantageNewsFeedItem]:
    TIME_STEP = timedelta(days=30)
    START_TIME = datetime(year=2024, month=1, day=1)
    END_TIME = datetime.now()

    assert len(tickers) <= TICKERS_LIMIT

    news: list[AlphaVantageNewsFeedItem] = []

    length = time_iterator_len(START_TIME, END_TIME, TIME_STEP)
    for start, end in tqdm(time_iterator(START_TIME, END_TIME, TIME_STEP), total=length):
        request = AlphaVantageNewsRequest(
            tickers=tickers,
            time_from=start,
            time_to=end,
            limit=1000,
        )
        response = request.query()
        data = response.json()
        result = AlphaVantageNewsResult(**data)
        news.extend(result.feed)

    return news


def get_news(symbol: str, time_from: datetime, time_to: datetime):
    request = AlphaVantageNewsRequest(
        tickers=[symbol], time_from=time_from, time_to=time_to, limit=1000
    )
    response = request.query()
    data = response.json()
    result = AlphaVantageNewsResult(**data)
    return result


if __name__ == "__main__":
    data = collect_overview()
    data = data.items()
    data = list(
        filter(
            lambda kv: "MarketCapitalization" in kv[1].keys()
            and kv[1]["MarketCapitalization"] != "None",
            data,
        )
    )
    data = [(k, int(v["MarketCapitalization"])) for k, v in data]
    data = sorted(data, key=lambda x: x[1], reverse=True)
    data = data[:6]
    tickers = [k for k, _ in data]
    news = collect_news(tickers=tickers)
    print()
