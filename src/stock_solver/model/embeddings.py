import torch
from math import log

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
    
    def forward(self, ticker_ids: torch.Tensor, length: int) -> torch.Tensor:
        embedding = self.embedding(ticker_ids.long())
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


class TemporalEmbedding(torch.nn.Module):
    def __init__(self, model_dim: int, dropout: float):
        super().__init__() # type: ignore
        self.emb_month = torch.nn.Embedding(13, model_dim)
        self.emb_day = torch.nn.Embedding(32, model_dim)
        self.emb_weekday = torch.nn.Embedding(7, model_dim)
        
        self.dropout = torch.nn.Dropout(dropout)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        month = self.emb_month(x[..., 0])
        day = self.emb_day(x[..., 1])
        weekday = self.emb_weekday(x[..., 2])
        return self.dropout(month + day + weekday)


class StaticEmbedding(torch.nn.Module):
    def __init__(self):
        # TODO
        super().__init__() # type: ignore
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # TODO
        return x
    

class DataEmbedding(torch.nn.Module):
    def __init__(
            self,
            value_dim_in: int,
            model_dim: int,
            num_tickers: int,
            dropout: float,
            max_seq_len: int,
        ):
        self.positional_embedding = PositionalEmbedding(model_dim, max_seq_len)
        self.value_embedding = ValueEmbedding(value_dim_in, model_dim)
        self.ticker_embedding = TickerEmbedding(num_tickers=num_tickers, dim=model_dim, dropout=dropout)
        self.temporal_embedding = TemporalEmbedding(model_dim=model_dim, dropout=dropout)
        self.dropout = torch.nn.Dropout(p=dropout)

    
    def forward(self, x: torch.Tensor, ticker_ids: torch.Tensor, x_marks: torch.Tensor) -> torch.Tensor:
        return (
            self.positional_embedding(x)
            + self.value_embedding(x)
            + self.ticker_embedding(ticker_ids)
            + self.temporal_embedding(x_marks)
        )