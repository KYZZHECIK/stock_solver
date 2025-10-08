import torch
import pandas as pd
import numpy as np

from dataclasses import dataclass
from typing import Dict, List, Tuple
from .apis.alpha_vantage_calls import populate_dataset

@dataclass
class WindowIndex:
    ticker_id: int
    start: int


class MultiTickerDataset(torch.utils.data.Dataset[Tuple[torch.Tensor, torch.Tensor, int]]):
    feature_cols: List[str] = ["open", "high", "low", "adjusted_close",]
    target_col: str = "close"

    def __init__(self, data: Dict[str, pd.DataFrame], lookback: int, horizon: int):
        super().__init__()

        self.data = data
        self.L = lookback
        self.H = horizon
        self.X: List[np.ndarray] = []
        self.Y: List[np.ndarray] = []
        self.dates: List[pd.DatetimeIndex] = []
        self.tickers = list(data.keys())
        self.win: List[WindowIndex] = []
        for ticker_id, ticker in enumerate(self.tickers):
            df = data[ticker]
            x = df[MultiTickerDataset.feature_cols].to_numpy(dtype=np.float32)
            y = df[MultiTickerDataset.target_col].to_numpy(dtype=np.float32)
            self.X.append(x)
            self.Y.append(y)
            self.dates.append(pd.DatetimeIndex(df.index))
            for date_index in range(self.L, len(df) - self.H):
                self.win.append(WindowIndex(ticker_id=ticker_id, start=date_index - self.L))

    @staticmethod
    def _date_mark(idx: pd.DatetimeIndex) -> torch.Tensor:
        month = idx.month.values
        day = idx.day.values
        weekday = idx.weekday.values
        mark = np.stack([month, day, weekday], axis=1)
        return torch.from_numpy(mark)
 
    def __len__(self) -> int:
        return len(self.win)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor, int, torch.Tensor, torch.Tensor]:
        # TODO: add normalization here
        window = self.win[idx]
        ticker_id, start = window.ticker_id, window.start

        x = self.X[ticker_id][start: start + self.L]
        y = self.Y[ticker_id][start + self.L: start + self.L + self.H] 
        enc_dates = self.dates[ticker_id][start: start + self.L]
        dec_dates = self.dates[ticker_id][start + self.L: start + self.L + self.H]

        x = torch.from_numpy(x)
        y = torch.from_numpy(y)
        enc_marks = MultiTickerDataset._date_mark(enc_dates)
        dec_marks = MultiTickerDataset._date_mark(dec_dates)
        return x, y, ticker_id, enc_marks, dec_marks


def collate(batch):
    xs, ys, ticker_ids, enc_marks, dec_marks = batch
    x = torch.stack(xs, dim=0)
    y = torch.stack(ys, dim=0)
    ticker_ids = torch.tensor(ticker_ids, dtype=torch.int64)
    enc_mark = torch.stack(enc_marks, dim=0).long()
    dec_mark = torch.stack(dec_marks, dim=0).long()
    return x, y, ticker_ids, enc_mark, dec_mark


if __name__ == '__main__':
    tickers = [
    "AAPL",
    "MSFT",
    # "AMZN",
    # "GOOG",
    # "GOOGL",
    # "META",
    ]

    data = populate_dataset(tickers)
    dataset = MultiTickerDataset(data, 10, 2)
    print(f"TEST | {dataset[0]}")

