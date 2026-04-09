# PINN / 代理模型模块结果汇总

## 当前定位

- 当前版本优先完成 **代理模型** 路线，而非直接进行高成本 PINN 训练。
- 训练集来自 `plate_3d` 已有半径扫描结果，并结合 Child-Langmuir 物理缩放生成第一版小样本。
- 同时保留了 1D 泊松方程 PINN 残差演示接口，用于后续扩展。

## 训练结果

- 数据集规模：67
- 训练集/验证集：53 / 14
- 训练轮数：200
- 最优验证损失：1.229123e-02
- MAE：5.948338e+03
- RMSE：8.210359e+03
- R²：0.992700

## 数据来源说明

- 训练样本类型：physics_guided_surrogate
- 生成样本数：64
- 锚点样本数：3
- 备注：训练集由 plate_3d 已有半径扫描结果和 Child-Langmuir 物理缩放共同构建，不等同于全量高精度数值求解。

## 输出文件

- `surrogate_dataset.csv`：训练数据集
- `surrogate_model.pt`：训练后的模型权重
- `pinn_loss.png`：损失曲线
- `pinn_prediction.png`：预测与真值对比图
- `pinn_residual_demo.png`：PINN 残差演示图
