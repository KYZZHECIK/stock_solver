from src.stock_solver.dataset.apis.alpha_vantage.requests import SymbolRequest

class InsiderTransactionsRequest(SymbolRequest):
    function: str = "INSIDER_TRANSACTIONS"