from src.stock_solver.dataset.apis.alpha_vantage_requests.symbol_request import AlphaVantageSymbolRequest
from typing import Literal

class AlphaVantageTimeSeriesDailyRequest(AlphaVantageSymbolRequest):
    function: str = "TIME_SERIES_DAILY_ADJUSTED"
    output_size: Literal["full", "compact"] = "compact"
    
    def params(self) -> dict[str, str]:
        params = super().params()
        params["outputsize"] = self.output_size
        return params