from pydantic import BaseModel
from typing import Any
from src.stock_solver.dataset.apis.alpha_vantage_results.result import AlphaVantageResult

class AlphaVantageNewsTickerSentiment(BaseModel):
    ticker: str
    relevance_score: str
    ticker_sentiment_score: str
    ticker_sentiment_label: str

class AlphaVantageNewsFeedItem(BaseModel):
    ticker_sentiment: list[AlphaVantageNewsTickerSentiment]

class AlphaVantageNewsResult(AlphaVantageResult):
    items: int
    sentiment_score_definition: str
    relevance_score_definition: str
    feed: list[AlphaVantageNewsFeedItem]

    @classmethod
    def empty(cls):
        return cls(
            items=0,
            sentiment_score_definition="",
            relevance_score_definition="",
            feed=[],
        )

    @classmethod
    def _is_invalid_data(cls, data: dict[str, Any]) -> bool:
        # If no articles were found, API returns OK response with error message in "Information"
        return not data or "Information" in data