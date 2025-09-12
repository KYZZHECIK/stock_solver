from .symbol_request import SymbolRequest

class OverviewRequest(SymbolRequest):
    function: str = "OVERVIEW"