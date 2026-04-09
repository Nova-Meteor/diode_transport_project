from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import torch
from torch import nn

from pinn.dataset import build_surrogate_dataset
from pinn.model import MLPRegressor, PoissonPINNDemo, StandardScaler


def _set_seed(seed: int) -> None:
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.set_num_threads(1)


def _split_dataset(x: torch.Tensor, y: torch.Tensor, ratio: float, seed: int):
    n = x.shape[0]
    gen = torch.Generator().manual_seed(seed)
    idx = torch.randperm(n, generator=gen)
    n_train = max(1, int(n * ratio))
    train_idx = idx[:n_train]
    val_idx = idx[n_train:]
    if val_idx.numel() == 0:
        val_idx = train_idx[-1:].clone()
    return (x[train_idx], y[train_idx]), (x[val_idx], y[val_idx])


def _save_dataset_csv(rows: list[dict[str, float]], path: Path) -> None:
    if not rows:
        return
    with path.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _plot_loss(history: list[dict[str, float]], path: Path) -> None:
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot([h['epoch'] for h in history], [h['train_loss'] for h in history], label='train')
    ax.plot([h['epoch'] for h in history], [h['val_loss'] for h in history], label='val')
    ax.set_xlabel('Epoch')
    ax.set_ylabel('MSE Loss')
    ax.set_title('Surrogate model loss history')
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def _plot_prediction(y_true: np.ndarray, y_pred: np.ndarray, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(5.5, 5))
    ax.scatter(y_true, y_pred, alpha=0.8)
    low = float(min(np.min(y_true), np.min(y_pred)))
    high = float(max(np.max(y_true), np.max(y_pred)))
    ax.plot([low, high], [low, high], linestyle='--')
    ax.set_xlabel('True current limit density')
    ax.set_ylabel('Predicted current limit density')
    ax.set_title('Prediction vs truth')
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def _plot_pinn_demo(output_dir: Path) -> dict[str, float]:
    x = torch.linspace(0.0, 1.0, 128).unsqueeze(1)
    model = PoissonPINNDemo()
    residual = model.residual(x).detach().cpu().numpy().reshape(-1)
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(x.detach().cpu().numpy().reshape(-1), residual)
    ax.set_xlabel('x')
    ax.set_ylabel('Residual')
    ax.set_title('PINN placeholder residual before training')
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(output_dir / 'pinn_residual_demo.png', dpi=160)
    plt.close(fig)
    return {
        'residual_mean_abs': float(np.mean(np.abs(residual))),
        'residual_max_abs': float(np.max(np.abs(residual))),
    }


def run_pinn_workflow(config: dict[str, Any], project_root: Path, output_dir: Path) -> dict[str, Any]:
    general = config.get('general', {})
    train_cfg = config.get('train', {})
    model_cfg = config.get('model', {})
    seed = int(general.get('random_seed', 42))
    _set_seed(seed)

    dataset = build_surrogate_dataset(config, project_root)
    rows = [
        {
            dataset.feature_names[0]: float(a),
            dataset.feature_names[1]: float(b),
            dataset.feature_names[2]: float(c),
            dataset.target_name: float(t),
        }
        for (a, b, c), (t,) in zip(dataset.x, dataset.y, strict=True)
    ]
    _save_dataset_csv(rows, output_dir / 'surrogate_dataset.csv')

    x = torch.tensor(dataset.x, dtype=torch.float32)
    y = torch.tensor(dataset.y, dtype=torch.float32)
    (x_train, y_train), (x_val, y_val) = _split_dataset(x, y, float(train_cfg.get('train_ratio', 0.8)), seed)
    x_scaler = StandardScaler.fit(x_train)
    y_scaler = StandardScaler.fit(y_train)
    x_train_s = x_scaler.transform(x_train)
    x_val_s = x_scaler.transform(x_val)
    y_train_s = y_scaler.transform(y_train)
    y_val_s = y_scaler.transform(y_val)

    model = MLPRegressor(
        input_dim=int(model_cfg.get('input_dim', 3)),
        hidden_dim=int(model_cfg.get('hidden_dim', 64)),
        num_layers=int(model_cfg.get('num_layers', 4)),
        output_dim=int(model_cfg.get('output_dim', 1)),
        activation=str(model_cfg.get('activation', 'tanh')),
    )
    optimizer = torch.optim.Adam(model.parameters(), lr=float(train_cfg.get('lr', 1e-3)))
    criterion = nn.MSELoss()
    epochs = int(train_cfg.get('epochs', 300))

    history: list[dict[str, float]] = []
    best_val = float('inf')
    best_state = None
    for epoch in range(1, epochs + 1):
        model.train()
        optimizer.zero_grad()
        pred_train = model(x_train_s)
        loss = criterion(pred_train, y_train_s)
        loss.backward()
        optimizer.step()
        train_loss = float(loss.item())
        model.eval()
        with torch.no_grad():
            val_loss = float(criterion(model(x_val_s), y_val_s).item())
        history.append({'epoch': epoch, 'train_loss': train_loss, 'val_loss': val_loss})
        if val_loss < best_val:
            best_val = val_loss
            best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}

    if best_state is not None:
        model.load_state_dict(best_state)

    model.eval()
    with torch.no_grad():
        pred_all = y_scaler.inverse_transform(model(x_scaler.transform(x))).cpu().numpy()
    true_all = y.cpu().numpy()

    mae = float(np.mean(np.abs(pred_all - true_all)))
    rmse = float(np.sqrt(np.mean(np.square(pred_all - true_all))))
    ss_res = float(np.sum(np.square(pred_all - true_all)))
    ss_tot = float(np.sum(np.square(true_all - np.mean(true_all))))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else float('nan')

    _plot_loss(history, output_dir / 'pinn_loss.png')
    _plot_prediction(true_all.reshape(-1), pred_all.reshape(-1), output_dir / 'pinn_prediction.png')
    pinn_demo = _plot_pinn_demo(output_dir)

    if bool(config.get('output', {}).get('save_model', True)):
        torch.save(
            {
                'model_state_dict': model.state_dict(),
                'x_scaler': x_scaler.to_dict(),
                'y_scaler': y_scaler.to_dict(),
                'feature_names': dataset.feature_names,
                'target_name': dataset.target_name,
                'config': config,
            },
            output_dir / 'surrogate_model.pt',
        )

    summary = {
        'module': 'pinn',
        'mode': config.get('data', {}).get('mode', 'surrogate'),
        'dataset_size': int(x.shape[0]),
        'train_size': int(x_train.shape[0]),
        'val_size': int(x_val.shape[0]),
        'epochs': epochs,
        'best_val_loss': best_val,
        'mae': mae,
        'rmse': rmse,
        'r2': r2,
        'feature_names': dataset.feature_names,
        'target_name': dataset.target_name,
        'dataset_metadata': dataset.metadata,
        'pinn_demo': pinn_demo,
        'note': '当前完成的是基于 plate_3d 小样本与 CL 物理缩放构建的代理模型，并保留了 PINN 残差演示接口。',
    }

    with (output_dir / 'pinn_summary.json').open('w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    with (output_dir / 'loss_history.json').open('w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)
    with (output_dir / 'dataset_metadata.json').open('w', encoding='utf-8') as f:
        json.dump(dataset.metadata, f, ensure_ascii=False, indent=2)

    with (output_dir / 'summary.md').open('w', encoding='utf-8') as f:
        f.write('# PINN / 代理模型模块结果汇总\n\n')
        f.write('## 当前定位\n\n')
        f.write('- 当前版本优先完成 **代理模型** 路线，而非直接进行高成本 PINN 训练。\n')
        f.write('- 训练集来自 `plate_3d` 已有半径扫描结果，并结合 Child-Langmuir 物理缩放生成第一版小样本。\n')
        f.write('- 同时保留了 1D 泊松方程 PINN 残差演示接口，用于后续扩展。\n\n')
        f.write('## 训练结果\n\n')
        f.write(f'- 数据集规模：{summary["dataset_size"]}\n')
        f.write(f'- 训练集/验证集：{summary["train_size"]} / {summary["val_size"]}\n')
        f.write(f'- 训练轮数：{epochs}\n')
        f.write(f'- 最优验证损失：{best_val:.6e}\n')
        f.write(f'- MAE：{mae:.6e}\n')
        f.write(f'- RMSE：{rmse:.6e}\n')
        f.write(f'- R²：{r2:.6f}\n\n')
        f.write('## 数据来源说明\n\n')
        f.write(f'- 训练样本类型：{dataset.metadata["dataset_kind"]}\n')
        f.write(f'- 生成样本数：{dataset.metadata["num_generated_samples"]}\n')
        f.write(f'- 锚点样本数：{dataset.metadata["num_anchor_samples"]}\n')
        f.write(f'- 备注：{dataset.metadata["note"]}\n\n')
        f.write('## 输出文件\n\n')
        f.write('- `surrogate_dataset.csv`：训练数据集\n')
        f.write('- `surrogate_model.pt`：训练后的模型权重\n')
        f.write('- `pinn_loss.png`：损失曲线\n')
        f.write('- `pinn_prediction.png`：预测与真值对比图\n')
        f.write('- `pinn_residual_demo.png`：PINN 残差演示图\n')

    return summary
