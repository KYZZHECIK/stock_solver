from src.stock_solver.dataset.apis.alpha_vantage.requests import SymbolRequest

class TimeSeriesWeekRequest(SymbolRequest):
    function: str = "TIME_SERIES_WEEKLY"