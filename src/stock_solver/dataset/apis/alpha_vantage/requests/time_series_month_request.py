from .symbol_request import SymbolRequest

class TimeSeriesMonthRequest(SymbolRequest):
    function: str = "TIME_SERIES_MONTHLY"