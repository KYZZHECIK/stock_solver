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

class TokenEmbedding(torch.nn.Module):
    # TODO
    ...