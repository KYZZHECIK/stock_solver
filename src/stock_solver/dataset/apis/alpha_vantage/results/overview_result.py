from .result import Result
from pydantic import Field, field_validator


MIN_MARKET_CAPITALIZATION = 1_000_000_000


class OverviewResult(Result):
    asset_type: str = Field(alias="AssetType")
    market_capitalization: int = Field(alias="MarketCapitalization")

    @field_validator("asset_type")
    @classmethod
    def _is_common_stock(cls, v: str):
        if not v or v != "Common Stock":
            raise ValueError("Ticker is not a common stock")
        return v
    
    @field_validator("market_capitalization")
    @classmethod
    def _is_significant_mc(cls, v: int):
        if v < MIN_MARKET_CAPITALIZATION:
            raise ValueError("Ticker has market cap below 1 mil")
        return v