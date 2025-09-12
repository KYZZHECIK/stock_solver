from src.stock_solver.dataset.apis.alpha_vantage.requests import SymbolRequest
from typing import Literal

class TimeSeriesDailyRequest(SymbolRequest):
    function: str = "TIME_SERIES_DAILY_ADJUSTED"
    output_size: Literal["full", "compact"] = "compact"
    
    def params(self) -> dict[str, str]:
        params = super().params()
        params["outputsize"] = self.output_size
        return params