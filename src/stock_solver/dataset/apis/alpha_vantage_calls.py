from datetime import date, datetime, timedelta
from typing import Generator, Dict

from joblib import Memory
from tqdm import tqdm

from src.stock_solver.dataset.apis.alpaca import get_assets

import stock_solver.dataset.apis.alpha_vantage as AV

TICKERS_LIMIT = 500
memory = Memory(".alpha_vantage_cache", verbose=0)

# @memory.cache
def collect_overview(symbols:list[str]):
    data: Dict[str, Dict[str, str]] = {}
    for s in tqdm(symbols):
        request = AV.OverviewRequest(symbol=s)
        try:
            result = request.query()
        except ValueError:
            print(f"Failed to fetch overview for {s}, skipping.")
            continue
        if j := result.json():
            data[s] = j
    return data

# @memory.cache
def collect_insider_transactions(symbols: list[str]):
    data: Dict[str, AV.InsiderTransactionsResult] = {}
    for symbol in tqdm(symbols):
        request = AV.InsiderTransactionsRequest(symbol=symbol)
        try: 
            response = request.query()
        except ValueError:
            print(f"Failed to fetch insider transactions for {symbol}, skipping.")
            continue
        transactions = response.json()
        result = AV.InsiderTransactionsResult.parse(transactions)
        data[symbol] = result
    return data

# @memory.cache
def collect_timeseries_day(symbols: list[str]):
    data: dict[str, AV.TimeSeriesResult] = {}
    for symbol in tqdm(symbols):
        request = AV.TimeSeriesDailyRequest(symbol=symbol)
        try:
            response = request.query()
        except ValueError:
            print(f"Failed to fetch timeseries daily for {symbol}, skipping.")
            continue
        timeseries = response.json()
        result = AV.TimeSeriesResult.parse(timeseries)
        data[symbol] = result
    return data
        
# @memery.cache
def collect_timeseries_intraday(symbols: list[str], interval: AV.Interval, month: date):
    data: dict[str, AV.TimeSeriesResult] = {}
    for symbol in tqdm(symbols):
        request = AV.TimeSeriesIntradayRequest(symbol=symbol, interval=interval, month=month)
        try: 
            response = request.query()
        except ValueError:
            print(f"Failed to fetch timeseries intradaily for {symbol}, skipping.")
            continue
        timeseries = response.json()
        result = AV.TimeSeriesResult.parse(timeseries)
        data[symbol] = result
    return data

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


# @memory.cache
def collect_news(tickers: list[str]):
    TIME_STEP = timedelta(days=30)
    START_TIME = datetime(year=2023, month=1, day=1)
    END_TIME = datetime.now()
    tickers = tickers[: TICKERS_LIMIT]
    assert len(tickers) <= TICKERS_LIMIT

    news: list[AV.NewsFeedItem] = []

    length = time_iterator_len(START_TIME, END_TIME, TIME_STEP)
    for start, end in tqdm(time_iterator(START_TIME, END_TIME, TIME_STEP), total=length):
        request = AV.NewsRequest(
            tickers=tickers,    # FIXME, trying to find articles with ALL the tickers inside, 
            time_from=start,    # which is pretty much impossible with 500+ tickers.
            time_to=end,        # Consider switching to news per ticket
            limit=1000,
        )
        try:
            response = request.query()
            data = response.json()
            result = AV.NewsResult.parse(data)
            news.extend(result.feed)
        except ValueError:
            print(f"Failed to fetch news for {tickers} from {start} till {end}, skipping.")
    return news


def get_news(symbol: str, time_from: datetime, time_to: datetime):
    request = AV.NewsRequest(
        tickers=[symbol], time_from=time_from, time_to=time_to, limit=1000
    )
    response = request.query()
    data = response.json()
    result = AV.NewsResult.parse(data)
    return result

if __name__ == "__main__":
    data = collect_timeseries_intraday(["IBM"], "60min", date(2022, 5, 1))
    print(data)
    # data = collect_overview()
    # data = data.items()
    # data = list(
    #     filter(
    #         lambda kv: "MarketCapitalization" in kv[1].keys()
    #         and kv[1]["MarketCapitalization"] != "None",
    #         data,
    #     )
    # )
    # data = [(k, int(v["MarketCapitalization"])) for k, v in data]
    # data = sorted(data, key=lambda x: x[1], reverse=True)
    # tickers = [k for k, _ in data]
    # print(tickers)
    # news = collect_news(tickers=tickers)
    # print(news)
    
