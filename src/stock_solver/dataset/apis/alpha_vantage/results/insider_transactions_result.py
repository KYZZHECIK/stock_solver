from pydantic import BaseModel 
from typing import Literal
from .result import Result

class InsiderTransaction(BaseModel):
    transaction_date: str
    ticker: str
    executive: str
    executive_title: str
    security_type: str
    acquisition_or_disposal: Literal["A", "D"]
    shares: str
    share_price: str

class InsiderTransactionsResult(Result):
    data: list[InsiderTransaction] = []