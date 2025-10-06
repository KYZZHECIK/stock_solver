from math import log
import torch

class FFN(torch.nn.Module):
    def __init__(self, dim: int, expansion: int):
        super().__init__() # type: ignore
        self.layers = torch.nn.Sequential(
            torch.nn.Linear(dim, dim * expansion),
            torch.nn.ReLU(),
            torch.nn.Linear(dim * expansion, dim)
        )
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.layers(x)


class Distillation(torch.nn.Module):
    def __init__(self):
        super().__init__() # type: ignore
        # TODO    

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # TODO 
        return x


class PositionalEmbedding(torch.nn.Module):
    pe: torch.Tensor

    def __init__(self, dim: int, len: int):
        super().__init__() # type: ignore
        pe = torch.zeros(len, dim).float()
        pe.requires_grad = False
        pos = torch.arange(len).float().unsqueeze(1)
        div = torch.exp(torch.arange(0, dim, 2) * (-log(10000) / dim))
        pe[:, 0::2] = torch.sin(pos * div)
        pe[:, 1::2] = torch.cos(pos * div)
        self.register_buffer("pe", pe.unsqueeze(0))
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.pe[:, :x.size(1), :]

class TickerEmbedding(torch.nn.Module):
    def __init__(self, num_tickers: int, dim: int, dropout: float):
        super().__init__() # type: ignore
        self.embedding = torch.nn.Embedding(num_tickers, dim)
        torch.nn.init.normal_(self.embedding.weight, std=0.3)
        self.drop = torch.nn.Dropout(dropout)
    
    def forward(self, x: torch.Tensor, length: int) -> torch.Tensor:
        embedding = self.embedding(x.view(-1))
        embedding = embedding.unsqueeze(1).expand(-1, length, -1) # [B, L, D]
        return self.drop(embedding)

class ValueEmbedding(torch.nn.Module):
    def __init__(self, dim_in: int, dim_out: int):
        super().__init__() # type: ignore
        self.layer = torch.nn.Conv1d(
            in_channels=dim_in,
            out_channels=dim_out,
            kernel_size=3,
            padding=1,
            padding_mode='circular'
        )
        torch.nn.init.kaiming_uniform_(self.layer.weight)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # [B, L, in] -> [B, in, L] -> conv -> [B, out, L] -> [B, L, out]
        return self.layer(x.transpose(1, 2)).transpose(1, 2)