from src.stock_solver.dataset.apis.alpha_vantage.requests import SymbolRequest
from ..types import OutputSize, Interval

from datetime import date
from typing import Optional

class TimeSeriesIntradayRequest(SymbolRequest):
    function: str = "TIME_SERIES_INTRADAY"
    interval: Interval 
    adjusted: bool = True
    extended_hours: bool = True
    outputsize: OutputSize = "full"
    month: Optional[date]
    
    def params(self) -> dict[str, str]:
        params = super().params()
        params["interval"] = self.interval
        params["adjusted"] = str(self.adjusted)
        params["extended_hours"] = str(self.extended_hours)
        params["outputsize"] = self.outputsize
        if self.month is not None:
            time_str = "%Y-%m" #converting to YYYY-MM
            params["month"] = self.month.strftime(time_str)
        return params
        




