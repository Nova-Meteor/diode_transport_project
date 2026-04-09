from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Dict

import yaml

AVAILABLE_MODULES = ("plate_3d", "tip_plane", "cross_field", "pinn")
PROJECT_ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="基于深度学习的二极管电子输运特性研究：统一运行入口"
    )
    parser.add_argument(
        "--module",
        type=str,
        choices=AVAILABLE_MODULES,
        help="要运行的模块名称",
    )
    parser.add_argument(
        "--config",
        type=str,
        help="对应模块的 YAML 配置文件路径",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="显示可用模块列表并退出",
    )
    return parser.parse_args()


def load_config(config_path: str) -> Dict[str, Any]:
    path = Path(config_path)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    if not path.exists():
        raise FileNotFoundError(f"配置文件不存在: {path}")

    with path.open("r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    if not isinstance(config, dict):
        raise ValueError("配置文件格式错误：顶层必须是字典")

    return config


def ensure_output_dir(config: Dict[str, Any]) -> Path | None:
    output_cfg = config.get("output", {})
    save_dir = output_cfg.get("save_dir")
    if not save_dir:
        return None

    path = Path(save_dir)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    path.mkdir(parents=True, exist_ok=True)
    return path


def print_header(module: str, config_path: str) -> None:
    print("=" * 60)
    print("二极管电子输运项目：统一运行入口")
    print(f"当前模块: {module}")
    print(f"配置文件: {config_path}")
    print("=" * 60)


def run_plate_3d(config: Dict[str, Any]) -> None:
    print("[plate_3d] 三维平板有限差分模块占位运行成功。")
    print("后续将在此接入：网格构建、非线性泊松方程、SOR、电场计算、割线法搜索。")
    print(f"网格规模: {config.get('grid', {})}")
    print(f"几何参数: {config.get('geometry', {})}")


def run_tip_plane(config: Dict[str, Any]) -> None:
    print("[tip_plane] 针尖-平板 MC/MD 模块占位运行成功。")
    print("后续将在此接入：发射几何、粒子推进、离散库仑作用、自洽循环。")
    print(f"粒子参数: {config.get('particles', {})}")


def run_cross_field(config: Dict[str, Any]) -> None:
    print("[cross_field] 交叉场模块占位运行成功。")
    print("后续将在此接入：E-B 场运动积分器、轨迹输出、鞘层厚度估计接口。")
    print(f"场参数: {config.get('fields', {})}")


def run_pinn(config: Dict[str, Any]) -> None:
    print("[pinn] AI/PINN 模块占位运行成功。")
    print("后续将在此接入：代理模型训练、PINN 最小示例、损失曲线输出。")
    print(f"模型参数: {config.get('model', {})}")


def dispatch_module(module: str, config: Dict[str, Any]) -> None:
    if module == "plate_3d":
        run_plate_3d(config)
    elif module == "tip_plane":
        run_tip_plane(config)
    elif module == "cross_field":
        run_cross_field(config)
    elif module == "pinn":
        run_pinn(config)
    else:
        raise ValueError(f"未知模块: {module}")


def main() -> None:
    args = parse_args()

    if args.list:
        print("可用模块:")
        for name in AVAILABLE_MODULES:
            print(f"- {name}")
        return

    if not args.module or not args.config:
        raise SystemExit("请提供 --module 和 --config，或使用 --list 查看模块列表。")

    print_header(args.module, args.config)
    config = load_config(args.config)

    config_module = config.get("module")
    if config_module and config_module != args.module:
        raise ValueError(
            f"模块不匹配：命令行为 {args.module}，配置文件中为 {config_module}"
        )

    output_dir = ensure_output_dir(config)
    if output_dir is not None:
        print(f"输出目录已就绪: {output_dir}")

    dispatch_module(args.module, config)
    print("运行结束。")


if __name__ == "__main__":
    main()
