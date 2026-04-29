# RANSAC 算法实现问题

**日期：** 2026-04-26

**问题：** 当前 RANSAC 算法的实现是错误的，不是真正的 RANSAC 雷达误差检测算法

---

## 当前错误实现

**位置：** `backend/app/utils/error_analysis/algorithms/ransac/algorithm.py`

**当前流程：**
```python
def _ransac_analyze(self, matched_groups, radar_positions):
    for group in matched_groups:
        # 问题1：对经纬度做线性回归
        ransac = RANSACRegressor()
        X = lats.reshape(-1, 1)  # 纬度
        y = lons  # 经度
        ransac.fit(X, y)
        inlier_mask = ransac.inlier_mask_

    # 问题2：然后调用梯度下降计算误差，和 MRRA 完全一样
    error_calc.calculate_radar_errors(inlier_groups, radar_positions)
```

**问题分析：**

1. **线性回归的对象错误**：RANSAC 应该对**系统误差参数**（方位角偏差、距离偏差）建模，而不是对经纬度做线性回归

2. **筛选后的数据没有特殊处理**：即使筛选出了 inlier_groups，`calculate_radar_errors` 内部还是自己用梯度下降重新计算，不会利用 RANSAC 的筛选结果

3. **和梯度下降法没有本质区别**：最终都是用梯度下降优化，RANSAC 那一步完全是形式主义

---

## 正确的 RANSAC 思想

**核心思想：** 找到"最大一致集"——哪些雷达站的观测是一致的（内点），哪些站偏离了一致性（外点/故障站）

**正确的 RANSAC 流程：**

### 步骤 1：计算几何中心

对于每个匹配组（同一时刻多站观测）：
- 计算所有站观测的几何中心（质心）
- 计算每个站与中心的偏差

### 步骤 2：RANSAC 识别故障站

对于每个匹配组：
1. **随机选择子集**：随机选择几个站作为"假设内点"
2. **用内点计算系统误差**：基于内点站估计 Δazimuth, Δrange, Δelevation
3. **验证其他站**：用这个误差模型预测其他站的观测位置
4. **计算残差**：预测位置 vs 实际位置的偏差
5. **判定内外点**：残差小于阈值的为内点，大于阈值的为外点
6. **重复迭代**：重复 N 次，找到内点数量最多的那次

### 步骤 3：统计故障站

- 统计每个站在所有匹配组中被判定为外点的次数
- 外点比例超过阈值（如 50%）的站判定为故障站

### 步骤 4：计算最终误差

- 只使用健康站（内点）的数据
- 用梯度下降或加权最小二乘计算最终误差

---

## 测试数据情况

测试数据包含：
- 健康站（数据正确）
- 故障站（数据有偏差）

需要 RANSAC 能够：
1. 正确识别出哪些站是故障站
2. 用健康站的数据计算准确的系统误差

---

## 状态

**已实现** - 创建了新的启发式 RANSAC 算法 `ransac_heuristic`

---

## 新算法实现

**位置：** `backend/app/utils/error_analysis/algorithms/ransac_heuristic/`

**核心流程：**
```
对每个匹配组：
    1. 计算几何中心（所有站观测的平均位置）
    2. 计算每个站与中心的偏差
    3. 按偏差排序：[0.001, 0.002, 0.003, 0.02, 0.25, 0.3]
    4. 检测差值突变点（前3个差值小，后3个差值突然变大）
    5. 突变点之前是健康站，之后是故障站

统计所有匹配组中每个站被判定为故障站的次数
外点比例 > 阈值的站 → 判定为故障站
```

**算法特点：**
- 不依赖随机采样
- 通过偏差排序 + 差值突变检测来识别故障站
- 只用健康站的数据计算最终误差


## 最新说明

**日期：** 2026-04-26

### 当前进度

1. **ransac_heuristic（启发式 RANSAC）已实现**，代码位置 `backend/app/utils/error_analysis/algorithms/ransac_heuristic/`，但尚未完整测试（task #12 因数据库重复键错误未能完成验证）

2. **传统 RANSAC 待重写**，当前 `ransac/algorithm.py` 仍是错误实现（对经纬度做线性回归），需要按照正确的 RANSAC 流程重写

3. **迭代寻优（梯度下降/MRRA）已存在**，需要配合 RANSAC 使用（RANSAC 先识别故障站并剔除，再用迭代寻优计算精确误差）

### 待完成工作

#### 1. 修复 ransac_heuristic 的 bug
- 清理 task #12 的旧数据（`ErrorResult`, `MatchGroup`, `TrackInterpolatedPoint`, `TrackSegment`），解决重复键问题
- 重新运行 `ransac_heuristic` 测试，验证故障站识别效果
- 当前测试结果全部判为健康站，可能需要：调低 `jump_threshold`、确认测试数据中确实有故障站

#### 2. 重写传统 RANSAC（`ransac/algorithm.py`）
目标：实现真正的随机采样 RANSAC，作为启发式 RANSAC 的对比算法

核心流程：
- 对每个匹配组，随机选 2 个站作为假设内点
- 基于这 2 个站估计系统误差（Δazimuth, Δrange, Δelevation）
- 用该误差模型预测其他站的位置，计算残差
- 残差 < 阈值的为内点，> 阈值的为外点
- 迭代 N 次，选内点最多的那次
- 统计每个站的外点比例，判断是否为故障站
- 只用健康站计算最终误差

难点：
- 从 2 个站出发估计系统误差的数学方法（非梯度下降）
- 需要确定合适的残差阈值和迭代次数
- 随机选 2 个站选到健康站+健康站的概率问题

#### 3. 三种算法对比测试
- 用同一份测试数据（含已知故障站），分别运行三种算法
- 对比故障站识别准确率、误差计算精度、运行时间
- 验证汇报文档中的结论

### 已知 bug
- task #12 保存结果时出现 `Duplicate entry` 数据库错误（外键冲突）
- 另见 `docs/问题/RANSAC算法实现问题.md` → 当前错误实现部分

---

## 参考

- sklearn.linear_model.RANSACRegressor 的正确用法
- RANSAC 在计算机视觉中的经典应用（基础矩阵估计、点云配准等）
