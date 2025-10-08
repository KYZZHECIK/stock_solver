import torch
import math

class ProbSparseAttention(torch.nn.Module):
    def __init__(self, factor: float, dropout: float = 0.1, eps: float = 1e-9):
        super().__init__() # type: ignore

        self.factor = factor
        self.dropout = torch.nn.Dropout(dropout)
        self.eps = eps

    def forward(self, Q: torch.Tensor, K: torch.Tensor, V: torch.Tensor) -> torch.Tensor:
        _, L_q, dim = Q.shape
        
        scores = get_scores(Q, K, dim)
        M = get_sparsity_measure(scores)

        top_idx = get_topk_queries(L_q, M, self.factor, self.eps)
        top_idx_exp = top_idx.unsqueeze(-1).expand(-1, -1, dim)
        Q_sparse = torch.gather(Q, dim=1, index=top_idx_exp)

        scores_sparse = get_scores(Q_sparse, K, dim)

        attention = torch.softmax(scores_sparse, dim=-1)
        attention = self.dropout(attention)

        context_sparse = attention @ V
        V_mean = V.mean(dim=1, keepdim=True)

        context = V_mean.expand(-1, L_q, -1).clone()
        context.scatter_(1, top_idx_exp, context_sparse)

        return context

class AttentionLayer(torch.nn.Module):
    def __init__(self, dim: int, heads: int, factor: float, attn_dropout: float = 0.1, proj_dropout: float = 0.1):
        super().__init__() # type: ignore
        self.dim, self.heads = dim, heads
        self.dh = dim // heads
        self.Q_proj = torch.nn.Linear(dim, dim)
        self.K_proj = torch.nn.Linear(dim, dim)
        self.V_proj = torch.nn.Linear(dim, dim)
        self.prob_attention = ProbSparseAttention(factor, attn_dropout)
        self.out = torch.nn.Linear(dim, dim)
        self.drop = torch.nn.Dropout(proj_dropout)
    
    def project(self, projection: torch.nn.Linear, x: torch.Tensor) -> torch.Tensor:
        B, L, _ = x.shape
        matrix: torch.Tensor = projection(x).view(B, L, self.heads, self.dh)
        matrix = matrix.permute(0, 2, 1, 3).contiguous().view(B*self.heads, L, self.dh)
        return matrix

    def forward(self, x: torch.Tensor):
        B, L, D = x.shape
        Q = self.project(self.Q_proj, x)
        K = self.project(self.K_proj, x)
        V = self.project(self.V_proj, x)

        context: torch.Tensor = self.prob_attention(Q, K, V)
        context = context.view(B, self.heads, L, self.dh)
        context = context.permute(0, 2, 1, 3).contiguous().view(B, L, D)

        return self.drop(self.out(context))

def get_sparsity_measure(scores: torch.Tensor) -> torch.Tensor:
    M_max, _ = scores.max(dim=-1)
    M_mean = scores.mean(dim=-1)
    return M_max - M_mean

def get_scores(Q: torch.Tensor, K: torch.Tensor, dim: int) -> torch.Tensor:
    return (Q @ K.transpose(-2, -1)) * (1 / math.sqrt(dim))

def get_topk_queries(L_q: int, M: torch.Tensor, factor: float, eps: float) -> torch.Tensor:
    k = min(L_q, max(1, int(factor * math.log(L_q + eps)))) 
    _, top_idx = torch.topk(M, k, dim=-1, largest=True, sorted=False)
    return top_idx