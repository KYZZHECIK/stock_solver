from .symbol_request import SymbolRequest

class TimeSeriesWeekRequest(SymbolRequest):
    function: str = "TIME_SERIES_WEEKLY"