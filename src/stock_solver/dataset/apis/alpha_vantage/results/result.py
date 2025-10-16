from pydantic import BaseModel, ConfigDict, model_validator
from typing import Any, ClassVar
from ..errors import APIError

class Result(BaseModel):
    error_keys: ClassVar[frozenset[str]] = frozenset({"error", "error message", "information", "note"})
    model_config = ConfigDict(extra="ignore")
    
    @model_validator(mode="before")
    @classmethod
    def _is_invalid_data(cls, data: Any) -> Any:
        if not data:
            raise TypeError("Data is null")
        if {str(key).lower() for key in dict(data)} & cls.error_keys:
            raise APIError("Error has occured!", data=data)
        return data