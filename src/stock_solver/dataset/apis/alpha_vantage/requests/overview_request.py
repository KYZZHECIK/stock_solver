from src.stock_solver.dataset.apis.alpha_vantage.requests import SymbolRequest

class OverviewRequest(SymbolRequest):
    function: str = "OVERVIEW"