from .symbol_request import SymbolRequest

class InsiderTransactionsRequest(SymbolRequest):
    function: str = "INSIDER_TRANSACTIONS"