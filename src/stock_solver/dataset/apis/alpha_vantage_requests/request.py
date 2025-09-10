from pydantic import BaseModel
import requests
from requests import Response, Request, Session
from src.stock_solver.dataset.utils import api_keys

api_key = api_keys().alpha_vantage_api
class AlphaVantageRequest(BaseModel):
    function: str
    apikey: str = api_key

    def params(self) -> dict[str, str]:
        return {
            "function": self.function,
            "apikey": self.apikey,
        }

    def query(self) -> Response:
        base_url = "https://www.alphavantage.co/query"
        params = self.params()
        # req = Request("GET", base_url, params=params)
        # prepped = Session().prepare_request(req)
        # print(f"TEST | {prepped.url}")
        response = requests.get(base_url, params=params)
        if not response.ok:
            raise ValueError(f"Error fetching data from Alpha Vantage: {response.reason}")
        return response