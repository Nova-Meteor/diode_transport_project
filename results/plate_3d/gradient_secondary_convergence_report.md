# 中心梯度次级量收敛报告（改进版）

## 1. 为什么需要改口径

在极限电流搜索中，`center_gradient` 本身就是根搜索目标，因此在 `J=J_lim` 处评估它会受到根求解残差支配，作为次级 QoI 并不稳健。

为得到更适合 Richardson / GCI 的次级量，本轮改用：

- `center_gradient_probe = center_gradient(J = 0.95 * J_lim)`

也就是在略低于极限电流的固定相对电流位置评估阴极中心梯度。这个量既保留物理意义，又避免“被强行搜索到接近 0”带来的病态性。

## 2. 三层统一 refinement ratio 网格组

- 网格组：[9, 13, 19]
- 统一 refinement ratio：r21 = 1.5, r32 = 1.5

## 3. Richardson / GCI 结果

- 观测收敛阶 p = 1.1473553091666904
- Richardson 外推值 = 182511.97600138604 V/m
- Fine-grid GCI = 12.14533468529358 %
- Coarse-grid GCI = 20.520716127682018 %
- 渐近区检查比 = 1.0610693864403582

## 4. 结论

相较于直接使用 `center_gradient(J_lim)`，新的 `center_gradient_probe` 已明显更接近可用于网格收敛分析的次级量：

- 观测阶为正；
- 渐近区检查比接近 1；
- 细网格 GCI 已降到约一个量级可接受的范围。

因此，后续论文正文中建议将“中心梯度次级量”的网格收敛验证口径写为 `center_gradient_probe`，而将 `center_gradient(J_lim)` 保留为极限电流搜索残差监控量。
