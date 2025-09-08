from datetime import datetime, timedelta
from typing import Generator, Dict

from joblib import Memory
from tqdm import tqdm

from src.stock_solver.dataset.apis.alpaca import get_assets

from stock_solver.dataset.apis.alpha_vantage_requests import(
    AlphaVantageOverviewRequest,
    AlphaVantageNewsRequest,
    AlphaVantageInsiderTransactionsRequest,
    AlphaVantageTimeSeriesDailyRequest,
)

from stock_solver.dataset.apis.alpha_vantage_results import(
    AlphaVantageNewsResult,
    AlphaVantageNewsFeedItem,
    AlphaVantageInsiderTransactionsResult,     
)

TICKERS_LIMIT = 500
memory = Memory(".alpha_vantage_cache", verbose=0)

@memory.cache
def collect_overview():
    assets = get_assets()
    symbols = [a.symbol for a in assets]
    data: Dict[str, Dict[str, str]] = {}
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

@memory.cache
def collect_insider_transactions(symbols: list[str]):
    data: Dict[str, AlphaVantageInsiderTransactionsResult] = {}
    for symbol in tqdm(symbols):
        request = AlphaVantageInsiderTransactionsRequest(symbol=symbol)
        try: 
            response = request.query()
        except ValueError:
            print(f"Failed to fetch insider transactions for {symbol}, skipping.")
            continue
        transactions = response.json()
        result = AlphaVantageInsiderTransactionsResult.parse(transactions)
        data[symbol] = result
    return data

# @memory.cache
# def collect_timeseries_daily(symbols: list[str]):
#     data = {}
#     # for symbol in tqdm(symbols):
        

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


@memory.cache
def collect_news(tickers: list[str]):
    TIME_STEP = timedelta(days=30)
    START_TIME = datetime(year=2023, month=1, day=1)
    END_TIME = datetime.now()
    tickers = tickers[: TICKERS_LIMIT]
    assert len(tickers) <= TICKERS_LIMIT

    news: list[AlphaVantageNewsFeedItem] = []

    length = time_iterator_len(START_TIME, END_TIME, TIME_STEP)
    for start, end in tqdm(time_iterator(START_TIME, END_TIME, TIME_STEP), total=length):
        request = AlphaVantageNewsRequest(
            tickers=tickers,    # FIXME, trying to find articles with ALL the tickers inside, 
            time_from=start,    # which is pretty much impossible with 500+ tickers.
            time_to=end,        # Consider switching to news per ticket
            limit=1000,
        )
        try:
            response = request.query()
            data = response.json()
            result = AlphaVantageNewsResult.parse(data)
            news.extend(result.feed)
        except ValueError:
            print(f"Failed to fetch news for {tickers} from {start} till {end}, skipping.")
    return news


def get_news(symbol: str, time_from: datetime, time_to: datetime):
    request = AlphaVantageNewsRequest(
        tickers=[symbol], time_from=time_from, time_to=time_to, limit=1000
    )
    response = request.query()
    data = response.json()
    result = AlphaVantageNewsResult.parse(data)
    return result

if __name__ == "__main__":
    data = collect_insider_transactions(["IBM"])
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
    
