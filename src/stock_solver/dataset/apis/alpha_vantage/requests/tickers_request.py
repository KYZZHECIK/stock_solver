from src.stock_solver.dataset.apis.alpha_vantage.requests import Request

class TickersRequest(Request):
    tickers: list[str]

    def params(self) -> dict[str, str]:
        params = super().params()
        ticker_sep = "," if len(self.tickers) > 1 else ""
        params["tickers"] = ticker_sep.join(self.tickers)
        return params