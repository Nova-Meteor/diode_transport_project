# 全面自查与补漏洞报告

生成时间：2026-04-08 15:33:33

## 1. 自查范围

本次检查覆盖以下内容：

- `src/main.py` 统一入口是否真实调用各模块
- `plate_3d` / `tip_plane` / `cross_field` / `pinn` 四个模块是否可以从命令行启动
- `run_all.sh` 是否能顺序调起全部模块
- 结果文件、图像文件、JSON 摘要文件是否能正常写出
- README 与总表是否与当前工程状态一致

## 2. 本次发现并修复的问题

### 已修复问题 1：`main.py` 仍为占位分发

- 现象：`python src/main.py --module plate_3d --config ...` 只打印占位信息，不执行真实计算。
- 影响：文档与实际行为不一致，无法作为统一入口使用。
- 修复：已将 `main.py` 改回真实分发，分别调用：
  - `fdm_3d.workflow.run_plate_3d_workflow`
  - `mc_md.self_consistent_loop.run_tip_plane_simulation`
  - `cross_field.eb_motion.run_cross_field_simulation`
  - `pinn.train.run_pinn_workflow`

### 已修复问题 2：`plate_3d` 默认参数下复现成本偏高

- 现象：默认搜索与网格规模较大时，主模块运行时间偏长，不利于本地快速回归。
- 修复：已将默认配置调整为快速演示规模：`21 x 21 x 21` 网格，并缩减默认搜索迭代与半径扫描规模。
- 结果：当前默认配置下，`plate_3d` 可在约 10 秒量级完成一次完整演示运行。

### 已修复问题 3：`pinn` 数据集读取与当前 JSON 结构不兼容

- 现象：`pinn` 模块假定 `radius_sweep.json` 为带 `items` 字段的字典，但当前实际文件为列表。
- 修复：`src/pinn/dataset.py` 已兼容“列表”和“带 `items` 的字典”两种结构。
- 结果：`pinn` 已可正常训练并输出损失曲线、预测图和模型权重。

## 3. 命令行回归结果

以下命令均已实际运行通过：

```bash
python src/main.py --list
python src/main.py --module plate_3d --config configs/plate_3d.yaml
python src/main.py --module tip_plane --config configs/tip_plane.yaml
python src/main.py --module cross_field --config configs/cross_field.yaml
python src/main.py --module pinn --config configs/pinn.yaml
./run_all.sh
```

## 4. 当前各模块运行结果

- `plate_3d`: `J_CL = 2.333902e+05 A/m²`, `J_lim = 3.017905e+05 A/m²`, `J_lim / J_CL = 1.293073`
- `tip_plane`: `透射比例 = 1.000000`, `平均最终能量 = 716.815524 eV`
- `cross_field`: `平均最终能量 = 4.294703 eV`, `Larmor 半径 = 6.966603e-06 m`
- `pinn`: `数据集规模 = 67`, `R² = 0.992846`

## 5. 当前仍保留的已知限制

- `plate_3d` 仍属于第一版工程实现，适合趋势展示，不宜直接作为论文级高精度数值结论。
- `tip_plane` 的外加场仍为简化近似，而非完整旋转椭球解析场。
- `cross_field` 的鞘层厚度和截止频率仍是接口级估计，尚未接入严格自洽模型。
- `pinn` 当前主体仍是代理模型，正式 PINN 训练与物理损失项尚未展开。

## 6. 结论

经过本轮全面自查，当前工程已经从“部分文档领先于代码”修正为“代码入口、配置、结果文件和结果说明基本一致”。
对于课程项目 / 日内汇报 / 第一版演示来说，这一版已经具备：

- 可运行
- 可展示
- 可继续开发
- 可作为下一阶段补强的基础
