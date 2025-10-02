import torch
import stock_solver.dataset.apis.alpha_vantage as AV
import pandas as pd
import numpy as np

from dataclasses import dataclass
from typing import Dict, List, Tuple

@dataclass
class WindowIndex:
    ticker_id: int
    start: int


class MultiTickerDataset(torch.utils.data.Dataset[Tuple[torch.Tensor, torch.Tensor, int]]):
    feature_cols: List[str] = ["open", "high", "low", "adjusted_close",]
    target_col: str = "close"
    # TODO: Known features: Holidays, Day of the Week, Month of the year, etc
    # TODO: fixed ticker2id mapping

    def __init__(self, data: Dict[str, pd.DataFrame], lookback: int, horizon: int, train_stats = None):
        super().__init__()

        self.data = data
        self.L = lookback
        self.H = horizon
        self.X: List[np.ndarray] = []
        self.Y: List[np.ndarray] = []
        self.tickers = list(data.keys())
        self.win: List[WindowIndex] = []
        for ticker_id, ticker in enumerate(self.tickers):
            df = data[ticker]
            x = df[MultiTickerDataset.feature_cols].to_numpy(dtype=np.float32)
            y = df[MultiTickerDataset.target_col].to_numpy(dtype=np.float32)
            self.X.append(x)
            self.Y.append(y)
            for date_index in range(self.L, len(df) - self.H):
                self.win.append(WindowIndex(ticker_id=ticker_id, start=date_index - self.L))

    def __len__(self) -> int:
        return len(self.win)
    
    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor, int]:
        # TODO: add normalization here
        window = self.win[idx]
        ticker_id, start = window.ticker_id, window.start
        x = self.X[ticker_id][start: start + self.L]
        y = self.Y[ticker_id][start + self.L: start + self.L + self.H] 
        x = torch.from_numpy(x)
        y = torch.from_numpy(y)
        return x, y, ticker_id


if __name__ == '__main__':
    ...
