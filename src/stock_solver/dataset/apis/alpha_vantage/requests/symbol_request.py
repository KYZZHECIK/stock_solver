from .request import Request

class SymbolRequest(Request):
    symbol: str

    def params(self) -> dict[str, str]:
        params = super().params()
        params["symbol"] = self.symbol
        return params