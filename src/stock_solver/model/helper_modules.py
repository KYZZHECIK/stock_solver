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