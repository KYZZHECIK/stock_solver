from torch.utils.data import Dataset, DataLoader
from typing import Optional
import stock_solver.dataset.apis.alpha_vantage as AV

import pandas as pd

class TimeSeriesDataset(Dataset):
    def __init__(self):
        ...
    
    def __len__(self):
        ...
    
    def __getitem__(self, idx: int):
        ...

def build_features(symbol: str, start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
    # TODO: I want this to return a DataFrame with columns for OCHLV values, news_sentiment_score,
    # and other useful metrics for a single ticker where we aggregate all the values on a daily index.



if __name__ == '__main__':
    ...
