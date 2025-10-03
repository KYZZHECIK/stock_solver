from pydantic import BaseModel
from typing import Any
from .result import Result

class NewsTickerSentiment(BaseModel):
    ticker: str
    relevance_score: str
    ticker_sentiment_score: str
    ticker_sentiment_label: str

class NewsFeedItem(BaseModel):
    time_published: str
    ticker_sentiment: list[NewsTickerSentiment]

class NewsResult(Result):
    items: int = 0
    sentiment_score_definition: str = ""
    relevance_score_definition: str = ""
    feed: list[NewsFeedItem] = []

    @classmethod
    def _is_invalid_data(cls, data: dict[str, Any]) -> bool:
        # If no articles were found, API returns OK response with error message in "Information"
        return not data or "Information" in data