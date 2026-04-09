# 环境与复现说明

本文档用于说明本项目当前推荐的运行环境、依赖安装方式、复现边界与结果口径。

---

## 1. 推荐环境

### 1.1 Python 版本

推荐：
- Python 3.11 或 3.12

当前工程在本轮整理中主要按以下口径验证：
- CPython 3.13 环境下已完成多轮运行与回归测试

为了兼顾依赖兼容性与本地复现便利，仍建议用户优先使用 Python 3.11/3.12。

### 1.2 操作系统

已考虑的运行方式：
- Linux / macOS shell
- Windows PowerShell

项目根目录同时提供：
- `run_all.sh`
- `run_all.ps1`

---

## 2. 依赖说明

当前 `requirements.txt` 包含：

```txt
numpy
scipy
matplotlib
pyyaml
numba
torch
```

说明：
- `numpy / scipy / matplotlib / pyyaml` 为核心依赖
- `numba` 目前属于可选加速依赖
- `torch` 主要用于 `pinn` 模块

建议安装方式：

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Windows PowerShell：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

## 3. 复现边界说明

### 3.1 工程可复现

当前项目已经具备以下可复现条件：
- 统一入口 `src/main.py`
- 统一 YAML 配置文件
- 统一结果输出目录
- 基本 smoke/regression 测试
- 明确的活跃代码锁定说明 `ACTIVE_CODE_LOCK.md`

### 3.2 数值结果的复现边界

不同模块的复现口径并不完全相同：

#### `plate_3d`
- 可稳定复现主算例结果
- 可复现网格收敛分析与误差分析框架
- 高网格最细层计算成本较高，极限电流最细层结果仍可能受搜索预算影响

#### `tip_plane`
- 可稳定复现工程强化版轨迹、能谱与电压扫描结果
- 当前属于工程近似模型，不应误读为最终高精度针尖解析场模型

#### `cross_field`
- 可稳定复现交叉场汇报版轨道、漂移和磁场扫描图
- 当前模型仍是汇报级最小研究版，不是完整空间电荷-电磁强耦合模型

#### `pinn`
- 可稳定复现 surrogate 训练与 1D PINN demo
- 当前定位为主求解器辅助模块，而非替代主求解器

---

## 4. 随机性与可重复性

本项目中的随机性主要出现在：
- `tip_plane` 粒子初始化
- `pinn` 网络初始化与训练过程

当前工程已经在测试与轻量运行中尽量固定随机种子，用于降低重复运行差异。但以下情况仍可能带来轻微变化：
- PyTorch 版本差异
- BLAS / OpenMP 底层实现差异
- 操作系统调度差异

建议：
- 对需要写进报告的结果，固定一次正式运行并保留输出文件
- 不要把多次随机运行结果混写成同一组正式引用口径

---

## 5. 推荐复现层级

### 层级 A：快速确认工程可运行

```bash
python src/main.py --list
python src/main.py --module cross_field --config configs/cross_field.yaml
python src/main.py --module tip_plane --config configs/tip_plane.yaml
```

### 层级 B：复现主结果

```bash
python src/main.py --module plate_3d --config configs/plate_3d.yaml
python src/main.py --module pinn --config configs/pinn.yaml
```

### 层级 C：复现数值验证材料

```bash
python src/main.py --module plate_3d --config configs/plate_3d_convergence.yaml
```

### 层级 D：做工程完整性检查

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

---

## 6. 当前正式引用建议

若用于结题、汇报或项目说明，建议优先引用：

- `results/plate_3d/summary.md`
- `results/plate_3d/numerical_method_note.md`
- `results/plate_3d/error_budget.md`
- `results/plate_3d/grid_convergence_report.md`
- `results/tip_plane/summary.md`
- `results/cross_field/summary.md`
- `results/pinn/summary.md`

若用于说明“当前版本是什么”，建议同时引用：
- `ACTIVE_CODE_LOCK.md`
- `ENGINEERING_CLEANUP_NOTE.md`
- `results/summary_table.md`
- `results/all_results_index.md`

---

## 7. 当前版本的限制说明

尽管本项目已经形成稳定工程版，但以下内容仍应明确说明：

- `plate_3d` 高网格最细层的极限电流结果仍存在计算成本与搜索预算的制约
- `tip_plane` 尚未采用严格旋转椭球解析场
- `cross_field` 尚未纳入完整空间电荷-电磁场强耦合
- `pinn` 当前仍以辅助主线和展示物理约束训练为主

因此，当前项目适合被表述为：

> 已形成可运行、可展示、可继续扩展的研究工程版本，主线结果和数值验证框架已经建立，具备继续推进论文工作的基础。

