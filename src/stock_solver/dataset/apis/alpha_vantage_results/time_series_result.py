from pydantic import BaseModel, Field
from src.stock_solver.dataset.apis.alpha_vantage_results.result import AlphaVantageResult

class AlphaVantageOCHLCV(BaseModel):
    open: str = Field(alias="1. open")
    high: str = Field(alias="2. close")
    low: str # FIXME: figure out on using close or adjusted close, because intra daily doesnt have one
    close: str
    adjusted_close: str
    volume: str


class AlphaVantageTimeSeriesItem(BaseModel):
    item: dict[str, AlphaVantageOCHLCV]


class AlphaVantageTimeSeriesDailyResult(AlphaVantageResult):
    meta_data: dict[str, str] = {} # FIXME could have the issue of not parsing because of the weird aliasing from the API
    time_series: list[AlphaVantageTimeSeriesItem] = []
