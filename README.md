# 基于深度学习的二极管电子输运特性研究

## 1. 项目简介

本项目围绕空间电荷限制电流与电子输运问题，构建以下四类模块：

- **fdm_3d**：三维平板二极管有限差分模型，用于求解非线性泊松方程、电势分布、电场分布以及空间电荷限制电流极限值。
- **mc_md**：针尖-平板结构的蒙特卡洛/分子动力学最小框架，用于研究离散空间电荷效应、电子轨迹与能量展宽。
- **cross_field**：交叉电磁场电子输运最小框架，用于演示电子在电场和磁场共同作用下的轨道偏转行为。
- **pinn**：代理模型 / PINN 最小版，用于开展空间电荷问题的 AI 建模与参数预测。

当前版本重点完成了 `plate_3d` 主线结果、`tip_plane` 最小版 MC/MD，以及 `pinn` 代理模型最小训练流程。

---

## 2. 当前完成内容

- [x] 项目目录结构初始化
- [x] 依赖文件 `requirements.txt`
- [x] 统一参数配置文件 `configs/*.yaml`
- [x] 统一运行入口 `src/main.py`
- [x] `plate_3d`：第一版主结果与图表整理
- [x] `tip_plane`：针尖-平板 MC/MD 最小示例
- [ ] `cross_field`：当前工程未保留源码入口
- [x] `pinn`：AI/PINN 最小训练示例

---

## 3. 运行方法

```bash
python src/main.py --list
python src/main.py --module tip_plane --config configs/tip_plane.yaml
python src/main.py --module pinn --config configs/pinn.yaml
```

---

## 4. pinn 模块说明

当前 `pinn` 模块优先实现的是 **代理模型** 路线，而不是直接进行高成本 PINN 训练。

- 输入特征：`gap`、`voltage`、`emitter_radius`
- 预测目标：`current_limit_density`
- 训练数据：由 `plate_3d` 已有半径扫描结果与 Child-Langmuir 物理缩放共同生成
- 网络结构：全连接 MLP
- 输出结果：损失曲线、预测对比图、训练集 CSV、模型权重，以及一个 PINN 残差演示图

说明：当前训练集不是全量高精度数值求解结果，而是用于项目当天交付的第一版 AI 接口。
