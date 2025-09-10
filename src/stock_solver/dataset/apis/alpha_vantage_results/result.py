from pydantic import BaseModel
from typing import Any, Self

class AlphaVantageResult(BaseModel):
    @classmethod
    def parse(cls, data: dict[str, Any]) -> Self:
        if cls._is_invalid_data(data):
            return cls()
        return cls(**data)

    @classmethod
    def _is_invalid_data(cls, data: dict[str, Any]) -> bool:
        """
        Optional Override. Return True if API response is invalid or empty.
        """
        return False

