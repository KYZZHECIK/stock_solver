import torch
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--batch_size", default=10, type=int)
parser.add_argument("--epochs", default=10, type=int)
parser.add_argument("--seed", default=42, type=int)


class StockSolver(torch.nn.Module):    
    def __init__(self) -> None:
        super().__init__() # type: ignore
        

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return x

if __name__ == '__main__':
    args = parser.parse_args([] if  "__file__" not in globals() else None)