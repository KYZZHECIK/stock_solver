import torch
import argparse
from .embeddings import DataEmbedding

parser = argparse.ArgumentParser()
parser.add_argument("--batch_size", default=10, type=int)
parser.add_argument("--epochs", default=10, type=int)
parser.add_argument("--seed", default=42, type=int)


class StockSolver(torch.nn.Module):    
    def __init__(
            self,
            enc_in: int,
            dec_in: int,
            model_dim: int,
            output_dim: int,
            num_tickers: int,
            dropout: float,
            max_seq_len: int,
        ) -> None:
        super().__init__() # type: ignore

        self.enc_embedding = DataEmbedding(enc_in, model_dim, num_tickers, dropout, max_seq_len)
        self.dec_embedding = DataEmbedding(dec_in, model_dim, num_tickers, dropout, max_seq_len)
        

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return x

if __name__ == '__main__':
    args = parser.parse_args([] if  "__file__" not in globals() else None)