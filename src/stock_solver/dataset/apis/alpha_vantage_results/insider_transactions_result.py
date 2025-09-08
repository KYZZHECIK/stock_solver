from pydantic import BaseModel 
from typing import Literal, Any

class AlphaVantageInsiderTransaction(BaseModel):
    transaction_date: str
    ticker: str
    executive: str
    executive_title: str
    security_type: str
    acquisition_or_disposal: Literal["A", "D"]
    shares: str
    share_price: str

class AlphaVantageInsiderTransactionsResult(BaseModel):
    data: list[AlphaVantageInsiderTransaction]

    @classmethod
    def parse(cls, data: dict[str, Any]):
        
        return cls(**data)
