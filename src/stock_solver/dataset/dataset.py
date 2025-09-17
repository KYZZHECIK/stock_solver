from dataclasses import dataclass
from torch.utils.data import Dataset, DataLoader
from typing import Optional
import stock_solver.dataset.apis.alpha_vantage as AV
import pandas as pd

@dataclass
class WindowConfig:
    enc_len: int
    label_len: int
    pred_len: int
    use_returns: bool = True


class MultiTickerDataset(Dataset):
    def __init__(self, panel: pd.DataFrame, cfg: WindowConfig):
        self.cfg = cfg

        raise NotImplementedError 

    def __len__(self) -> int:
        raise NotImplementedError
    
    def __getitem__(self, idx: int):
        raise NotImplementedError



if __name__ == '__main__':
    ...
