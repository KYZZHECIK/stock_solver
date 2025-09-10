from pydantic import BaseModel 
from typing import Literal
from src.stock_solver.dataset.apis.alpha_vantage_results.result import AlphaVantageResult

class AlphaVantageInsiderTransaction(BaseModel):
    transaction_date: str
    ticker: str
    executive: str
    executive_title: str
    security_type: str
    acquisition_or_disposal: Literal["A", "D"]
    shares: str
    share_price: str

class AlphaVantageInsiderTransactionsResult(AlphaVantageResult):
    data: list[AlphaVantageInsiderTransaction] = []
