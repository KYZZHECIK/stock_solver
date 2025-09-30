from torch.utils.data import Dataset
import stock_solver.dataset.apis.alpha_vantage as AV
import pandas as pd
import numpy as np

from dataclasses import dataclass
from typing import Dict, List

@dataclass
class WindowIndex:
    tkr_id: int
    start: int


class MultiTickerDataset(Dataset):
    feature_cols: List[str] = ["open", "high", "low", "adjusted_close",]
    target_col: str = "close"
    # TODO: Known features: Holidays, Day of the Week, Month of the year, etc

    def __init__(self, data: Dict[str, pd.DataFrame], lookback: int, horizon: int, train_stats = None):
        super().__init__()

        self.data = data
        self.L = lookback
        self.H = horizon
        
        self.X: List[np.ndarray] = []
        self.Y: List[np.ndarray] = []

        # TODO: compute stats on train split only (supply train_stats when building train set; reuse for val/test)
        self.stats = train_stats or {}
        
        self.tickers = list(data.keys())
        self.win: List[WindowIndex] = []
        for ticker_id, ticker in enumerate(self.tickers):
            df = data[ticker]
            x = df[MultiTickerDataset.feature_cols].to_numpy(dtype=np.float32)
            y = df[MultiTickerDataset.target_col].to_numpy(dtype=np.float32)

            # TODO: per ticker normalization / OR move normalization out and reuse it later

            self.X.append(x)
            self.Y.append(y)

            for date_index in range(self.L, len(df) - self.H):
                self.win.append(WindowIndex(tkr_id=ticker_id, start=date_index - self.L))


    def __len__(self) -> int:
        return len(self.win)
    
    def __getitem__(self, idx: int):
        # TODO: return self.win[idx] processed
        raise NotImplementedError


if __name__ == '__main__':
    ...
