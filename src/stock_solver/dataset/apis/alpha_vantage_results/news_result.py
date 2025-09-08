from pydantic import BaseModel
from typing import Any


class AlphaVantageNewsTickerSentiment(BaseModel):
    ticker: str
    relevance_score: str
    ticker_sentiment_score: str
    ticker_sentiment_label: str


class AlphaVantageNewsFeedItem(BaseModel):
    ticker_sentiment: list[AlphaVantageNewsTickerSentiment]


class AlphaVantageNewsResult(BaseModel):
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
    def parse(cls, data: dict[str, Any]):
        # If no articles were found, API returns OK response with error message in "Information"
        if data.get("Information"):
            return cls.empty()
        
        return cls(**data)
