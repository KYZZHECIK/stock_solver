from src.stock_solver.dataset.apis.alpha_vantage.requests import SymbolRequest, OutputSize

class TimeSeriesDailyRequest(SymbolRequest):
    function: str = "TIME_SERIES_DAILY_ADJUSTED"
    outputsize: OutputSize = "full"
    
    def params(self) -> dict[str, str]:
        params = super().params()
        params["outputsize"] = self.outputsize
        return params