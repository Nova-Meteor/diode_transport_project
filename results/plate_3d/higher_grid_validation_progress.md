# plate_3d 更高层网格验证：本轮进展说明

本轮工作的重点不是继续盲目增大最细网格，而是先把 **更高网格层的搜索成本压下来**，确保统一 refinement ratio 三层组在当前工程代码下能稳定复现。

## 1. 采取的改进

1. 将 `configs/plate_3d_convergence.yaml` 的收敛搜索参数收紧为 **seed-local 优先**：
   - `scan_factors = [1.0]`
   - `seed_window_factors = [0.98, 1.0, 1.02]`
   - `seed_expansion_ratio = 1.04`
   - `seed_expansion_steps = 3`
   - `pre_refine_subdivisions = 2`
   - `max_iter = 5`
2. 使 finer grid 更依赖上一层 `J_lim` 作为 continuation 种子，而不是每层都从头做全局粗扫。
3. 将“更高层网格验证”的目标先定为：**保证 17/25/37 三层高网格组全部能在当前配置下跑通并给出近零 root objective**。

## 2. 当前实测结果（统一 ratio 三层高网格组）

下面结果来自当前 `plate_3d_convergence.yaml` 收紧后的真实试跑：

| 网格 n | J_lim (A/m²) | root objective (V/m) | converged |
|---|---:|---:|---|
| 17 | 2.7646024283e+05 | 5.0649246621e+03 | True |
| 25 | 2.6671359203e+05 | -6.0960010446e+01 | True |
| 37 | 2.6407105196e+05 | -9.7874878733e+00 | True |

## 3. 观察

- `n=25` 和 `n=37` 的根目标值已明显接近 0，说明 continuation + 窄窗 seed 搜索对细网格层是有效的。
- `n=37` 相比前一版更容易进入“可用的近根求解”状态，说明更高网格验证的瓶颈主要在 **搜索策略**，而不仅仅是求解器本身。
- `n=17` 仍然偏粗，root objective 仍有一定偏差，因此后续正式 Richardson / GCI 报告中应继续以 `25/37/(更细层)` 为主。

## 4. 下一步建议

1. 在保持当前窄窗 seed 搜索策略的前提下，继续尝试 `n=55` 作为补充 finest grid。
2. 若 `n=55` 仍然成本过高，优先加入 **coarse-to-fine 场分布 prolongation warm start**，再做 25/37/55 组的正式 Richardson / GCI 定稿。
3. 在正式论文稿中，可先把这一轮结果写成“higher-grid validation progress”，作为从 `17/25/37` 向 `25/37/55` 过渡的数值方法改进说明。
