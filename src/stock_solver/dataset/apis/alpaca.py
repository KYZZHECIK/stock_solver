from typing import cast

from alpaca.trading import AssetClass, TradingClient, GetAssetsRequest, AssetStatus, Asset

from src.stock_solver.dataset.utils import api_keys

keys = api_keys()
alpaca_api_key, alpaca_secret_key = keys.alpaca_api, keys.alpaca_secret


def get_assets() -> list[Asset]:
    client = TradingClient(api_key=alpaca_api_key, secret_key=alpaca_secret_key)
    request = GetAssetsRequest(asset_class=AssetClass.US_EQUITY, status=AssetStatus.ACTIVE)

    data = cast(list[Asset], client.get_all_assets(request))

    return data
