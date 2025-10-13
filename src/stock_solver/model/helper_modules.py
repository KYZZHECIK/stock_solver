from typing import Optional
import torch

class FFN(torch.nn.Module):
    def __init__(self, model_dim: int, hidden_dim: int, dropout: float):
        super().__init__() # type: ignore
        self.layers = torch.nn.Sequential(
            torch.nn.Conv1d(model_dim, hidden_dim, 1),
            torch.nn.ReLU(),
            torch.nn.Dropout(dropout),
            torch.nn.Conv1d(hidden_dim, model_dim, 1),
        )
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.layers(x.transpose(1, 2)).transpose(1, 2)


class Distillation(torch.nn.Module):
    def __init__(self, model_dim: int):
        super().__init__() # type: ignore
        self.layers = torch.nn.Sequential(
            torch.nn.Conv1d(model_dim, model_dim, 3, padding=1, padding_mode="circular"),
            torch.nn.BatchNorm1d(model_dim),
            torch.nn.ELU(),
            torch.nn.MaxPool1d(kernel_size=3, stride=2, padding=1)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.layers(x.transpose(1, 2)).transpose(1, 2) # [B, L/2, D]


class EncoderLayer(torch.nn.Module):
    def __init__(self, attention: torch.nn.Module, model_dim: int, hidden_dim: int, dropout: float):
        super().__init__() # type: ignore
        self.attention = attention
        self.dropout = torch.nn.Dropout(dropout)
        self.norm1 = torch.nn.LayerNorm(model_dim)
        self.ffn = FFN(model_dim, hidden_dim, dropout)
        self.norm2 = torch.nn.LayerNorm(model_dim)

    def forward(
            self,
            x: torch.Tensor,
            key_padding_mask: Optional[torch.Tensor] = None,
            attn_mask: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        attn_out = self.attention(x, key_padding_mask, attn_mask)
        x = self.norm1(x + self.dropout(attn_out))
        y = self.ffn(x)
        x = self.norm2(x + y)
        return x
 

class DecoderLayer(torch.nn.Module):
    def __init__(self):
        super().__init__() # type: ignore
        
