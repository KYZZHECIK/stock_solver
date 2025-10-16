from pydantic import BaseModel, ConfigDict, Field
from typing import Any, List
from .result import Result


class NewsTickerSentiment(BaseModel):
    ticker: str
    relevance_score: str
    ticker_sentiment_score: str
    ticker_sentiment_label: str
    model_config = ConfigDict(extra="ignore")


class NewsFeedItem(BaseModel):
    time_published: str
    ticker_sentiment: list[NewsTickerSentiment]


class NewsResult(Result):
    items: int = 0
    sentiment_score_definition: str = ""
    relevance_score_definition: str = ""
    feed:List[NewsFeedItem] = Field(default_factory=List[NewsFeedItem])