from src.stock_solver.dataset.apis.alpha_vantage_requests.symbol_request import AlphaVantageSymbolRequest

class AlphaVantageOverviewRequest(AlphaVantageSymbolRequest):
    function: str = "OVERVIEW"