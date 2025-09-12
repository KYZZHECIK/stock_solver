from datetime import datetime
from src.stock_solver.dataset.apis.alpha_vantage.requests import TickersRequest

class NewsRequest(TickersRequest):
    function: str = "NEWS_SENTIMENT"
    time_from: datetime
    time_to: datetime
    limit: int

    def params(self) -> dict[str, str]:
        params = super().params()
        # convert to YYYYMMDDTHHMM
        time_str = "%Y%m%dT%H%M"
        params["time_from"] = self.time_from.strftime(time_str)
        params["time_to"] = self.time_to.strftime(time_str)
        params["limit"] = str(self.limit)
        params["sort"] = "EARLIEST"
        return params