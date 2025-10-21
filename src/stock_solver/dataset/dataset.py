import torch
import pandas as pd
import numpy as np

from dataclasses import dataclass
from typing import Dict, List, Tuple, TypeAlias
from .apis.alpha_vantage_calls import load_data

TrainElement: TypeAlias = Tuple[Tuple[torch.Tensor, torch.Tensor], Tuple[torch.Tensor, torch.Tensor], int]
TestElement: TypeAlias = Tuple[Tuple[torch.Tensor, torch.Tensor], torch.Tensor, int]
Element: TypeAlias = TrainElement | TestElement

@dataclass
class WindowIndex:
    ticker_id: int
    start: int


class MultiTickerDataset(torch.utils.data.Dataset[Element]):
    feature_cols: List[str] = ["open", "high", "low", "adjusted_close", "news_sentiment_wmean"]
    target_col: str = "close"

    def __init__(self, data: Dict[str, pd.DataFrame], lookback: int, horizon: int, is_test: bool = False):
        super().__init__()
        self.is_test = is_test

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
            self.dates.append(pd.DatetimeIndex(df.index))
            x = df[MultiTickerDataset.feature_cols].to_numpy(dtype=np.float32)
            self.X.append(x)
            if not is_test:
                y = df[MultiTickerDataset.target_col].to_numpy(dtype=np.float32)
                self.Y.append(y)
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

    def __getitem__(self, idx: int) -> Element:
        # TODO: add normalization here
        window = self.win[idx]
        ticker_id, start = window.ticker_id, window.start
        x = self.X[ticker_id][start: start + self.L]
        x = torch.from_numpy(x)
        enc_marks = MultiTickerDataset._date_mark(self.dates[ticker_id][start: start + self.L])
        dec_marks = MultiTickerDataset._date_mark(self.dates[ticker_id][start + self.L: start + self.L + self.H])
        if not self.is_test:
            y = self.Y[ticker_id][start + self.L: start + self.L + self.H]
            y = torch.from_numpy(y) 
            return (x, enc_marks), (y, dec_marks), ticker_id
        return (x, enc_marks), dec_marks, ticker_id


def collate(batch: List[Element]):
    xs, ys, ticker_ids, enc_marks, dec_marks = batch
    x = torch.stack(xs, dim=0)
    y = torch.stack(ys, dim=0)
    ticker_ids = torch.tensor(ticker_ids, dtype=torch.int64)
    enc_mark = torch.stack(enc_marks, dim=0).long()
    dec_mark = torch.stack(dec_marks, dim=0).long()
    return x, y, ticker_ids, enc_mark, dec_mark


if __name__ == '__main__':
    data = load_data()
    dataset = MultiTickerDataset(data, lookback=30, horizon=3)
    print(dataset[0])