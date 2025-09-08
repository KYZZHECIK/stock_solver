from pydantic import BaseModel
from abc import ABC, abstractmethod
from typing import Any, Self

class AlphaVantageResult(BaseModel, ABC):
    @staticmethod
    def is_invalid_data(data: dict[str, Any]) -> bool:
        return True

    @classmethod
    @abstractmethod
    def empty(cls) -> Self:
        raise NotImplementedError()

    @classmethod
    def parse(cls, data: dict[str, Any]) -> Self:
        if cls.is_invalid_data(data):
            return cls.empty()
        return cls(**data)

    @classmethod
    def _is_invalid_data(cls, data: dict[str, Any]) -> bool:
        """
        Optional Override. Return True if API response is valid and not empty.
        """
        return False

