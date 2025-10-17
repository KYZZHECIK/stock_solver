from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Any, Dict
from pydantic.functional_validators import model_validator

from .result import Result


class OHLCV(BaseModel):
    open: str
    high: str
    low: str
    close: str
    adjusted_close: Optional[str] = Field(default=None)
    volume: str

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    @model_validator(mode="before")
    @classmethod
    def _normalize_keys(cls, v: Any) -> Any:
        # API returns numbered keys for the values, e.g "1. open", etc
        # we use this to map the weird keys to normal field names
        keymap = {
            "1. open": "open", "open": "open",
            "2. high": "high", "high": "high",
            "3. low": "low",  "low": "low",

            "4. close": "close", "close": "close",
            "5. adjusted close": "adjusted_close",
            "adjusted close": "adjusted_close",
            "adjusted_close": "adjusted_close",

            "5. volume": "volume",
            "6. volume": "volume",
            "volume": "volume",
        }

        return {keymap.get(k, k): v for k, v in v.items()}

class TimeSeriesResult(Result):
    meta_data: Dict[str, str] = Field(default_factory=dict, alias="Meta Data")
    time_series: Dict[str, OHLCV] = Field(default_factory=dict)

    model_config = ConfigDict(populate_by_name=True, extra='ignore')

    @model_validator(mode="before")
    @classmethod
    def _extract_timeseries(cls, v: Any) -> Any:
        v = dict(v)
        if "Meta Data" in v and "meta_data" not in v:
            v["meta_data"] = v.pop("Meta Data")
        
        ts_key = next((k for k in v.keys() if k.startswith("Time Series")), None)
        if ts_key is not None and "time_series" not in v:
            v["time_series"] = v.pop(ts_key)
        
        return v