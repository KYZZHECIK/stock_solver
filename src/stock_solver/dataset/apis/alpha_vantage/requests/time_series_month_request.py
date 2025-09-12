from src.stock_solver.dataset.apis.alpha_vantage.requests import SymbolRequest

class TimeSeriesMonthRequest(SymbolRequest):
    function: str = "TIME_SERIES_MONTLHLY"