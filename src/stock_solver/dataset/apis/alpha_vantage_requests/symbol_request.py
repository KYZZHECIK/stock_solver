from src.stock_solver.dataset.apis.alpha_vantage_requests.request import AlphaVantageRequest

class AlphaVantageSymbolRequest(AlphaVantageRequest):
    symbol: str

    def params(self) -> dict[str, str]:
        params = super().params()
        params["symbol"] = self.symbol
        return params