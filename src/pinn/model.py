from __future__ import annotations

from dataclasses import dataclass

import torch
from torch import nn


class MLPRegressor(nn.Module):
    def __init__(self, input_dim: int, hidden_dim: int, num_layers: int, output_dim: int, activation: str = 'tanh'):
        super().__init__()
        if activation.lower() == 'relu':
            act_factory = nn.ReLU
        elif activation.lower() == 'gelu':
            act_factory = nn.GELU
        else:
            act_factory = nn.Tanh
        dims = [input_dim] + [hidden_dim] * (max(num_layers, 2) - 1) + [output_dim]
        layers: list[nn.Module] = []
        for in_dim, out_dim in zip(dims[:-2], dims[1:-1]):
            layers += [nn.Linear(in_dim, out_dim), act_factory()]
        layers.append(nn.Linear(dims[-2], dims[-1]))
        self.net = nn.Sequential(*layers)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


@dataclass
class StandardScaler:
    mean: torch.Tensor
    std: torch.Tensor

    @classmethod
    def fit(cls, x: torch.Tensor) -> 'StandardScaler':
        mean = x.mean(dim=0, keepdim=True)
        std = x.std(dim=0, keepdim=True, unbiased=False)
        std = torch.where(std < 1e-12, torch.ones_like(std), std)
        return cls(mean=mean, std=std)

    def transform(self, x: torch.Tensor) -> torch.Tensor:
        return (x - self.mean) / self.std

    def inverse_transform(self, x: torch.Tensor) -> torch.Tensor:
        return x * self.std + self.mean

    def to_dict(self) -> dict[str, list[float]]:
        return {
            'mean': self.mean.detach().cpu().numpy().reshape(-1).tolist(),
            'std': self.std.detach().cpu().numpy().reshape(-1).tolist(),
        }


class PoissonPINNDemo(nn.Module):
    def __init__(self, hidden_dim: int = 24):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(1, hidden_dim),
            nn.Tanh(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.Tanh(),
            nn.Linear(hidden_dim, 1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)

    def residual(self, x: torch.Tensor) -> torch.Tensor:
        x = x.requires_grad_(True)
        y = self.forward(x)
        dy = torch.autograd.grad(y, x, grad_outputs=torch.ones_like(y), create_graph=True)[0]
        d2y = torch.autograd.grad(dy, x, grad_outputs=torch.ones_like(dy), create_graph=True)[0]
        return d2y
