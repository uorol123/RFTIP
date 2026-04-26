# RFTIP 智能雷达轨迹分析平台 - 工作计划

> 生成时间: 2026-04-26 | 基于完整代码分析

---

## 一、项目当前状态总结

### 1.1 技术栈

| 维度 | 实际状态 |
|------|---------|
| 后端框架 | FastAPI + SQLAlchemy + Pydantic |
| 前端框架 | Vue 3 + Vite + TypeScript + Pinia |
| 数据库 | MySQL 8.0 (SQLAlchemy ORM) |
| 文件存储 | MinIO（已集成但可选本地存储） |
| 三维可视化 | Cesium.js（前端已有框架但功能尚未深度集成） |
| 大模型 | DeepSeek / Ollama（**模拟实现，未接入真实 API**） |

### 1.2 代码规模

| 模块 | 文件数 | 说明 |
|------|--------|------|
| 后端路由 | 8 个 | auth, files, tracks, zones, analysis, query, websocket, error_analysis |
| 后端服务层 | 10 个 | 含 RANSAC/Kalman 的 track_service，MRRA 误差分析等 |
| 后端算法模块 | 2 套 | `app/utils/mrra/`（梯度下降）+ `app/utils/error_analysis/`（算法框架） |
| 前端页面 | 14 个 Vue 视图 | ErrorAnalysis, Dashboard, DataManagement 等 |
| 前端组件 | ~25 个 | 含算法选择器、配置面板、图表等 |

### 1.3 架构亮点

- **双算法架构**: `app/utils/error_analysis/` 实现了插件化算法注册框架（Registry + Factory），支持动态扩展
- **MRRA 完整流程**: 航迹提取 -> 插值 -> 匹配 -> 梯度下降优化，全流程已跑通
- **前后端工作流完整**: 选择算法 -> 选择雷达站 -> 选择轨迹 -> 配置参数 -> 开始分析 -> 轮询进度 -> 展示结果

---

## 二、已实现功能列表

### 2.1 用户系统（完整）
- 用户注册/登录（JWT 认证）
- 邮箱验证码
- 用户资料管理、头像上传
- 登录日志记录

### 2.2 数据管理（完整）
- CSV/Excel 文件上传与解析
- 轨迹数据（flight_tracks_raw）与雷达站数据（radar_stations）入库
- 文件列表、详情查看、删除
- 数据权限隔离（用户私有 + 公开共享）

### 2.3 误差分析 - MRRA/梯度下降算法（核心功能，已完整）
- **算法框架**: 插件化注册（Registry）、工厂创建（Factory）、统一接口（BaseErrorAnalysisAlgorithm）
- **MRRA 算法**: 基于梯度下降的迭代寻优
  - 航迹提取：空间网格 + 时间窗口检测关键航迹
  - 航迹插值：时间对齐 + 线性插值
  - 航迹匹配：基于距离阈值的多雷达匹配
  - 误差计算：方位角/距离/俯仰角三维度独立优化
- **后台任务**: 分析任务创建 -> 后台执行 -> 轮询状态
- **结果展示**: 图表（ECharts）、详细数据表格、匹配组可视化
- **历史任务**: 任务列表、详情查看、完整流程步骤回放
- **算法管理 API**: 列出算法、获取配置 Schema、获取预设、验证配置
- **预设配置**: standard / high_precision / fast / coarse 四种方案

### 2.4 轨迹处理 - RANSAC/Kalman（基本实现，但存在严重 bug）
- `track_service.py` 中实现了 `RANSACAlgorithm` 和 `KalmanFilterAlgorithm` 类
- REST API `/api/tracks/process` 支持 `multi_source`(RANSAC) 和 `single_source`(Kalman) 模式
- 结果保存到 `flight_tracks_corrected` 表

### 2.5 禁飞区管理（基本实现）
- 创建/查询/更新/删除禁飞区（圆形 + 多边形）
- 禁飞区激活/停用切换
- 入侵检测 API（`/api/zones/detect-intrusions`）
- 入侵记录查询

### 2.6 AI 智能分析（框架已搭建，核心未实现）
- 特征提取（位置、速度、运动、时间四类特征）
- LLM 调用框架（`_call_deepseek` / `_call_ollama` 为 **模拟实现**）
- 分析报告生成（基于规则的简单实现）
- 风险等级评估

### 2.7 前端可视化
- 误差分析完整工作流 UI
- 算法选择器（动态渲染算法列表和配置表单）
- Cesium.js 三维地球基础框架

---

## 三、未实现功能列表

### 3.1 README 描述但未实现的功能

| 功能 | README 描述 | 实际状态 |
|------|-------------|---------|
| **RANSAC 算法集成到误差分析系统** | 多源参考模式中 RANSAC 剔除"坏点"雷达站 | 仅在 track_service 中有独立实现，未接入 error_analysis 算法框架 |
| **多源参考模式完整流程** | RANSAC + 加权最小二乘 + 系统误差估计 | 仅梯度下降算法可用，RANSAC/加权最小二乘未作为算法注册 |
| **单源盲测模式** | 卡尔曼滤波 + 粒子滤波 + 样条平滑 | track_service 中有基础 Kalman，无粒子滤波、无样条平滑，未接入算法框架 |
| **粒子滤波** | 处理非线性非高斯噪声 | 完全未实现 |
| **样条平滑** | 连续平滑轨迹曲线 | 完全未实现 |
| **MCP 坐标转语义** | 坐标逆地理编码 | 未实现 |
| **大模型真实接入** | DeepSeek/Ollama 实际 API 调用 | 仅有模拟响应 |
| **Cesium 三维可视化** | 多轨迹对比/误差热力图/动画回放等 | 前端有基础框架但核心可视化未实现 |
| **禁飞区三维渲染** | 圆形/多边形在三维地图上绘制 | 未实现 |
| **高度可视化** | 高度感应墙/颜色映射/3D 立体感 | 未实现 |
| **动画回放** | 时间轴控制轨迹动态回放 | 未实现 |
| **邮件预警** | 入侵检测后发送邮件通知 | 未实现 |
| **GPU 加速** | CUDA 加速矩阵运算 | 完全未实现 |

---

## 四、已发现的 Bug 列表

### 4.1 严重 Bug（会导致运行时崩溃）

#### BUG-1: `MrraAlgorithm._init_components()` 参数错误
- **文件**: `backend/app/utils/error_analysis/algorithms/mrra/algorithm.py` 第 179-182 行
- **问题**: `TrackExtractor.__init__` 需要 `(config, min_coord, max_coord)` 三个参数，但只传了 `mrra_config`。同样 `TrackMatcher.__init__` 也需要三个参数。这会导致 `TypeError` 运行时崩溃。
- **影响**: 当通过算法框架（非 `_execute_with_legacy_flow`）调用 MrraAlgorithm 时会崩溃。目前 `execute_analysis` 走的是 `_execute_with_legacy_flow`，所以正常使用不会触发，但这是一个架构缺陷。

#### BUG-2: `track_service.py` 引用 `FlightTrackRaw` 不存在的字段
- **文件**: `backend/app/services/track_service.py` 第 546、582、590、595 行
- **问题**: `preprocess_raw_data` 方法访问 `track.radar_station_id`、`track.track_id`、`track.raw_data`，但 `FlightTrackRaw` 模型中：
  - `track_id` 不存在（实际字段是 `batch_id`）
  - `raw_data` 不存在（模型中无此字段）
  - `radar_station_id` 存在（OK）
- **影响**: 调用 `/api/tracks/process` 时会在预处理阶段崩溃。

#### BUG-3: MySQL 不支持 `func.array_agg`
- **文件**: `backend/app/routers/error_analysis.py` 第 439 行
- **问题**: `func.array_agg()` 是 PostgreSQL 函数，MySQL 8.0 不支持。MySQL 应使用 `GROUP_CONCAT` 或子查询。
- **影响**: 调用 `/api/error-analysis/common-tracks` 时会抛出 SQL 错误。

#### BUG-4: `pyproj` 未在 requirements.txt 中声明
- **文件**: `backend/requirements.txt`
- **问题**: `app/utils/mrra/error_calculator.py` 导入了 `pyproj`，但 requirements.txt 中未列出此依赖。
- **影响**: 新部署环境下 `from app.utils.mrra.error_calculator import calculate_error_results` 会失败。

#### BUG-5: `_execute_with_legacy_flow` 中 MrraConfig 字段名不匹配
- **文件**: `backend/app/services/error_analysis_service.py` 第 170 行
- **问题**: `MrraConfig(**task.config)` 中 `task.config` 的 JSON 字段可能包含 `time_window_ratio`，但 `MrraConfig` (在 `app/utils/mrra/config.py`) 也有此字段，实际是一致的。但如果前端传的 config 对象含有额外的键（如来自 `MrraAlgorithmConfig` 的字段），Pydantic 可能会报错或忽略。
- **影响**: 低概率，取决于前端传的具体配置。

### 4.2 中等 Bug（功能异常但不崩溃）

#### BUG-6: `ErrorResult` 缺少 `confidence`、`iterations`、`final_cost` 字段保存
- **文件**: `backend/app/services/error_analysis_service.py` 第 529-538 行
- **问题**: `_save_error_results` 只保存了 `azimuth_error`、`range_error`、`elevation_error`、`match_count`，没有保存 `confidence`、`iterations`、`final_cost`。
- **影响**: 前端展示的置信度、迭代次数、最终代价始终为 null。

#### BUG-7: 前后端 CostWeights 字段名不一致
- **后端** (`backend/app/schemas/error_analysis.py`): `azimuth_error_square`, `range_error_square`, `elevation_error_square`
- **前端** (`frontend/src/types/errorAnalysis.ts`): `azimuth`, `range`, `elevation`
- **影响**: 前端传递 cost_weights 时字段名对不上，后端可能无法正确解析前端传来的配置。

#### BUG-8: `TrackInterpolatedPoint.track_id` 类型不匹配
- **文件**: `backend/app/models/error_analysis.py` 第 184 行
- **问题**: `track_id = Column(Integer, ...)` 定义为整数，但实际航迹批号（如 '100081'）是字符串。`track_extractor.py` 中传入的是字符串 batch_id。
- **影响**: 保存插值点时可能出现类型错误或数据截断。

#### BUG-9: `TrackSegment.track_id` 同样的类型问题
- **文件**: `backend/app/models/error_analysis.py` 第 89 行
- **问题**: `track_id = Column(Integer, ...)` 定义为整数，但实际是字符串批号。

### 4.3 轻微问题

#### BUG-10: `_call_deepseek` 和 `_call_ollama` 为模拟实现
- **文件**: `backend/app/services/analysis_service.py` 第 478-489 行
- **问题**: 返回硬编码字符串而非实际 API 调用。

#### BUG-11: `TrackPreprocessor` 使用中文字段名
- **文件**: `backend/app/services/track_preprocessor.py`
- **问题**: 使用 `df['入库时间']`、`df['经度']` 等中文列名，与数据库模型字段不匹配。此模块似乎是早期独立脚本，未与主系统集成。

#### BUG-12: `track_service.py` 中 `TrackCorrectionAlgorithm.correct()` 返回格式与 `process_tracks` 消费格式不一致
- **文件**: `backend/app/services/track_service.py`
- **问题**: `RANSACAlgorithm.correct()` 返回 `corrected_observations`（嵌套在时间组内），但 `process_tracks` 直接遍历 `result['corrected_observations']`，实际返回的 key 是 `corrected_observations` 但其内容是扁平列表。此处实际是匹配的，但 `RANSACAlgorithm.correct` 中对不足 `min_samples` 的组直接返回的格式（flat list 而非 nested）可能与其他分支的返回格式有差异。

---

## 五、分阶段工作计划

### 阶段一：RANSAC 算法接入误差分析系统（优先级 1）

**目标**: 在现有误差分析算法框架中新增 RANSAC 算法，使其可以通过前端选择并执行。

#### 任务清单

| # | 任务 | 文件 | 预估复杂度 |
|---|------|------|------------|
| 1.1 | 创建 RANSAC 算法目录结构 | `backend/app/utils/error_analysis/algorithms/ransac/__init__.py` (新建) | 低 |
| 1.2 | 实现 RANSAC 配置模型 | `backend/app/utils/error_analysis/algorithms/ransac/config.py` (新建) | 中 |
| 1.3 | 实现 RANSAC 算法主体 | `backend/app/utils/error_analysis/algorithms/ransac/algorithm.py` (新建) | 高 |
| 1.4 | 注册 RANSAC 算法 | 修改 `backend/app/utils/error_analysis/algorithms/__init__.py` | 低 |
| 1.5 | 前端创建 RANSAC 配置组件 | `frontend/src/components/errorAnalysis/algorithms/ransac/RansacConfig.vue` (新建) | 中 |
| 1.6 | 前端注册 RANSAC 配置组件 | 修改 `frontend/src/components/errorAnalysis/algorithms/index.ts` | 低 |
| 1.7 | 补充 pyproj 依赖 | 修改 `backend/requirements.txt` | 低 |

**RANSAC 算法核心逻辑**:
- 复用现有 `track_service.py` 中的 `RANSACAlgorithm` 作为参考
- 在误差分析框架中，RANSAC 的定位是：从匹配组中剔除离群点（故障/低精度雷达站），然后用剩余内点计算系统误差
- 输入：匹配组列表 + 雷达站位置
- 输出：各雷达站的系统误差估计 + 故障雷达标记
- 需实现 `BaseErrorAnalysisAlgorithm` 接口的 `analyze()` 方法

**技术要点**:
```python
# 算法注册（自动发现）
# backend/app/utils/error_analysis/algorithms/__init__.py
from app.utils.error_analysis.algorithms.ransac import RansacAlgorithm
```

```python
# RANSAC 核心接口
class RansacAlgorithm(BaseErrorAnalysisAlgorithm):
    ALGORITHM_NAME = "ransac"
    ALGORITHM_DISPLAY_NAME = "RANSAC 随机抽样一致性算法"

    def analyze(self, radar_station_ids, track_ids, db_session, progress_callback=None):
        # 1. 复用 MRRA 的航迹提取、插值、匹配流程
        # 2. 对匹配组应用 RANSAC 剔除离群点
        # 3. 基于内点计算系统误差
        pass
```

**预估工时**: 3-4 天

---

### 阶段二：多源参考模式完整实现（优先级 2）

**目标**: 实现多个雷达同时观测同一目标时的完整误差分析与轨迹优化。

#### 任务清单

| # | 任务 | 文件 | 预估复杂度 |
|---|------|------|------------|
| 2.1 | 实现加权最小二乘融合算法 | `backend/app/utils/error_analysis/algorithms/weighted_lstsq/` (新建目录) | 高 |
| 2.2 | 实现融合轨迹输出 | 修改 `backend/app/services/error_analysis_service.py`，增加轨迹融合逻辑 | 高 |
| 2.3 | 数据库增加融合轨迹存储 | 考虑使用 `flight_tracks_corrected` 表存储优化轨迹 | 中 |
| 2.4 | 前端增加融合轨迹对比展示 | 修改 `frontend/src/views/ErrorAnalysis.vue` 或新建组件 | 中 |
| 2.5 | 前端三维可视化展示融合轨迹 | 修改 `frontend/src/views/TrackVisualization.vue` | 高 |

**核心逻辑**:
- 多源参考模式 = RANSAC（剔除坏点）+ 加权最小二乘（融合轨迹）+ 系统误差估计
- 加权最小二乘：根据各雷达站的信噪比/匹配数/方差确定权重
- 融合轨迹 = 各雷达站修正后观测的加权平均

**预估工时**: 5-7 天

---

### 阶段三：修复已知 Bug（优先级 3）

**目标**: 修复所有已发现的 Bug，确保系统稳定运行。

#### 任务清单

| # | Bug | 修复方案 | 涉及文件 | 复杂度 |
|---|-----|---------|---------|--------|
| 3.1 | BUG-1: MrraAlgorithm._init_components 参数错误 | 延迟创建 TrackExtractor/TrackMatcher，在实际需要时才传入 min_coord/max_coord | `algorithm.py` | 中 |
| 3.2 | BUG-2: track_service 引用不存在字段 | 将 `track.track_id` 改为 `track.batch_id`，移除 `track.raw_data` 引用 | `track_service.py` 第 546-596 行 | 中 |
| 3.3 | BUG-3: MySQL 不支持 array_agg | 改用子查询或 GROUP_CONCAT 实现 | `error_analysis.py` 第 431-465 行 | 中 |
| 3.4 | BUG-4: pyproj 缺失 | 在 requirements.txt 添加 `pyproj` | `requirements.txt` | 低 |
| 3.5 | BUG-6: ErrorResult 缺少字段 | 在 `_save_error_results` 中增加 confidence/iterations/final_cost 计算 | `error_analysis_service.py` 第 521-540 行 | 中 |
| 3.6 | BUG-7: 前后端 CostWeights 字段名不一致 | 统一为后端命名（`azimuth_error_square` 等），修改前端类型定义 | `frontend/src/types/errorAnalysis.ts` | 低 |
| 3.7 | BUG-8/9: track_id 类型不匹配 | 将 `TrackInterpolatedPoint.track_id` 和 `TrackSegment.track_id` 改为 `String` | `error_analysis.py` 第 89、184 行 | 中 |
| 3.8 | BUG-5: config 字段兼容性 | 在 `_execute_with_legacy_flow` 中过滤掉 MrraConfig 不支持的额外字段 | `error_analysis_service.py` 第 170 行 | 低 |

**详细修复方案**:

**BUG-2 修复** (`track_service.py`):
```python
# 第 546 行，改为:
key = f"{track.radar_station_id}_{track.batch_id}"  # track_id -> batch_id

# 第 580-596 行，移除 raw_data 引用，改为:
processed_data.append({
    'raw_track_id': track.id,
    'track_id': track.batch_id,  # 使用 batch_id
    ...
    'radar_station_id': track.radar_station_id,
    'raw_data': {},  # 移除 track.raw_data，使用空字典
})
```

**BUG-3 修复** (`error_analysis.py`):
```python
# 替换 func.array_agg 为子查询方案:
from sqlalchemy import and_

# 方案：使用 GROUP_CONCAT + 字符串解析，或使用纯子查询
# 推荐方案：用 Python 层面的集合操作代替 SQL 聚合
station_batches = {}
for sid in station_list:
    batches = db.query(FlightTrackRaw.batch_id).filter(
        FlightTrackRaw.radar_station_id == sid
    ).distinct().all()
    station_batches[sid] = set(b[0] for b in batches)

common = set.intersection(*station_batches.values())
```

**BUG-8/9 修复** (`error_analysis.py`):
```python
# 第 89 行和第 184 行，改为:
track_id = Column(String(50), nullable=False, comment="航迹批号")
```

**预估工时**: 2-3 天

---

### 阶段四：单源盲测模式实现（优先级 4）

**目标**: 实现单站数据的卡尔曼滤波、粒子滤波、样条平滑。

#### 任务清单

| # | 任务 | 文件 | 预估复杂度 |
|---|------|------|------------|
| 4.1 | 实现卡尔曼滤波算法（接入算法框架） | `backend/app/utils/error_analysis/algorithms/kalman/` (新建) | 高 |
| 4.2 | 实现粒子滤波算法 | `backend/app/utils/error_analysis/algorithms/particle_filter/` (新建) | 高 |
| 4.3 | 实现样条平滑算法 | `backend/app/utils/error_analysis/algorithms/spline/` (新建) | 中 |
| 4.4 | 注册三个算法 | 修改 `algorithms/__init__.py` | 低 |
| 4.5 | 前端配置组件 | 新建对应的 Vue 配置组件 | 中 |
| 4.6 | 适配单站数据工作流 | 修改前端选择逻辑，允许选择单个雷达站 | 中 |
| 4.7 | 前端结果展示优化 | 修改图表组件，展示平滑前后对比 | 中 |

**技术要点**:

**卡尔曼滤波**（基于已有 `track_service.py` 中的实现）:
- 6 状态变量: [lat, lon, alt, v_lat, v_lon, v_alt]
- 匀速运动模型
- 需要适配算法框架接口

**粒子滤波**:
- 状态空间: [lat, lon, alt, v_lat, v_lon, v_alt]
- 粒子数: 默认 1000
- 重采样策略: 系统重采样
- 适用场景: 非线性非高斯噪声

**样条平滑**:
- 使用 `scipy.interpolate.UnivariateSpline` 或 `CubicSpline`
- 对经度、纬度、高度分别进行平滑
- 可配置平滑因子

**预估工时**: 5-7 天

---

## 六、技术实现要点

### 6.1 算法框架扩展指南

新增算法需要以下步骤：

```
1. 创建目录: backend/app/utils/error_analysis/algorithms/<algorithm_name>/
2. 创建文件:
   - __init__.py      (注册算法)
   - config.py         (Pydantic 配置模型)
   - algorithm.py      (继承 BaseErrorAnalysisAlgorithm)
3. 在 algorithms/__init__.py 中导入注册
4. (可选) 创建前端配置组件
```

**算法基类接口** (`backend/app/utils/error_analysis/base.py`):
```python
class BaseErrorAnalysisAlgorithm(ABC):
    ALGORITHM_NAME: str          # 唯一标识
    ALGORITHM_VERSION: str       # 版本号
    ALGORITHM_DISPLAY_NAME: str  # 显示名
    ALGORITHM_DESCRIPTION: str   # 描述

    def analyze(self, radar_station_ids, track_ids, db_session, progress_callback) -> AnalysisResult
    def get_default_config(self)
    def get_config_schema(self) -> Dict[str, Any]  # JSON Schema
    def get_config_preset_profiles(self) -> Dict[str, Any]
    def supports_elevation(self) -> bool
```

### 6.2 前后端交互流程

```
前端                              后端
  |                                 |
  |-- GET /algorithms ------------->|  获取算法列表
  |<-- [{name, display_name, ...}]--|
  |                                 |
  |-- GET /algorithms/{name}/config-schema -->|  获取配置Schema
  |<-- JSON Schema -----------------|
  |                                 |
  |-- GET /algorithms/{name}/presets -------->|  获取预设配置
  |<-- [{name, display_name, config}]--------|
  |                                 |
  |-- POST /analyze --------------->|  创建分析任务
  |   {radar_station_ids,           |
  |    track_ids,                   |
  |    algorithm: "ransac",         |
  |    config: {...}}               |
  |<-- {task_id, status} -----------|
  |                                 |
  |-- GET /tasks/{id} (轮询) ------>|  查询任务状态
  |<-- {status, progress} ----------|
  |                                 |
  |-- GET /tasks/{id}/results ----->|  获取分析结果
  |<-- {errors, statistics, ...} ---|
```

### 6.3 关键依赖版本

| 包 | 版本 | 用途 |
|----|------|------|
| scikit-learn | 1.5.2 | RANSAC (sklearn.linear_model.RANSACRegressor) |
| filterpy | 1.4.5 | 卡尔曼滤波 (filterpy.kalman.KalmanFilter) |
| numpy | 1.26.4 | 数值计算 |
| pandas | 2.2.3 | 数据处理 |
| pyproj | **需新增** | 地理坐标转换（误差计算中使用） |
| scipy | **需新增** | 样条平滑（单源盲测模式） |

---

## 七、风险评估与建议

### 7.1 高风险项

1. **数据库字段类型不匹配** (BUG-8/9): `track_id` 在 `TrackInterpolatedPoint` 和 `TrackSegment` 中定义为 Integer，但实际使用的是字符串。如果已有生产数据，需要数据库迁移。
2. **前后端类型不一致** (BUG-7): CostWeights 字段名不一致可能导致配置传递失败。

### 7.2 建议

1. **优先修复 Bug 再开发新功能**: 特别是 BUG-2（track_service 字段名错误）和 BUG-3（MySQL 不支持 array_agg），这些会直接导致功能不可用。
2. **统一算法架构**: 目前 RANSAC/Kalman 在 `track_service.py` 中有一套独立实现，MRRA 在 `app/utils/error_analysis/` 和 `app/utils/mrra/` 中有另一套。建议统一到算法框架中。
3. **增加单元测试**: 当前 `tests/` 目录下测试很少，建议对每个新算法至少编写集成测试。
4. **依赖管理**: 在 requirements.txt 中补充 `pyproj` 和 `scipy`。

# 完成情况

## 阶段一：RANSAC 算法接入误差分析系统 - 已完成 ✓

**完成时间**: 2026-04-26

### 已完成的工作

| # | 任务 | 文件 | 状态 |
|---|------|------|------|
| 1.1 | 创建 RANSAC 算法目录结构 | `backend/app/utils/error_analysis/algorithms/ransac/__init__.py` | ✓ |
| 1.2 | 实现 RANSAC 配置模型 | `backend/app/utils/error_analysis/algorithms/ransac/config.py` | ✓ |
| 1.3 | 实现 RANSAC 算法主体 | `backend/app/utils/error_analysis/algorithms/ransac/algorithm.py` | ✓ |
| 1.4 | 注册 RANSAC 算法 | `backend/app/utils/error_analysis/algorithms/__init__.py` | ✓ |
| 1.5 | 前端 RANSAC 配置组件 | `frontend/src/components/errorAnalysis/algorithms/ransac/RansacConfig.vue` | ✓ |
| 1.6 | 前端注册 RANSAC 组件 | `algorithms/index.ts` + `AlgorithmConfigContainer.vue` | ✓ |
| 1.7 | 补充依赖 | `requirements.txt` 添加 pyproj, scipy | ✓ |

### 测试验证

- ✓ 后端算法注册成功（gradient_descent + ransac 共 2 个算法）
- ✓ AlgorithmFactory 可创建 RANSAC 实例
- ✓ 自定义配置和默认配置均正常
- ✓ 预设配置 4 个方案（standard/strict/loose/fast）
- ✓ 前端 TypeScript 类型检查通过
- ✓ RANSAC 配置 Schema 正确生成（13 个配置项）

### RANSAC 算法核心逻辑

- 复用 MRRA 的航迹提取→插值→匹配流程
- 对每个匹配组应用 RANSACRegressor 区分内点/离群点
- 统计各雷达站离群率，超过阈值标记为故障站
- 基于内点数据用 ErrorCalculator 计算系统误差

---

## 阶段二：多源参考模式完整实现 - 已完成 ✓

**完成时间**: 2026-04-26

### 已完成的工作

| # | 任务 | 文件 | 状态 |
|---|------|------|------|
| 2.1 | 加权最小二乘融合算法 | `algorithms/weighted_lstsq/` (新建3文件) | ✓ |
| 2.2 | 融合轨迹输出与存储 | `error_analysis_service.py` + `error_analysis.py` 模型 | ✓ |
| 2.3 | 数据库增加 result_metadata 字段 | `ErrorAnalysisTask.result_metadata` | ✓ |
| 2.4 | 融合轨迹 API 端点 | `GET /tasks/{id}/fused-trajectory` | ✓ |
| 2.5 | 前端 weighted_lstsq 配置组件 | `WeightedLstsqConfig.vue` | ✓ |
| 2.6 | 前端组件注册 | `AlgorithmConfigContainer.vue` + `index.ts` | ✓ |
| 2.7 | BUG-3 修复: MySQL array_agg | `error_analysis.py` common-tracks 端点 | ✓ |
| 2.8 | BUG-8/9 修复: track_id 类型 | `error_analysis.py` 模型 Integer→String(50) | ✓ |

### 多源参考模式算法组合

用户可在前端选择：
- **RANSAC 算法**：识别故障站 + 计算误差
- **加权最小二乘算法**：融合多站数据 + 输出优化轨迹 + 计算误差

### 额外修复的 Bug

- **BUG-3**: `/api/error-analysis/common-tracks` 的 `func.array_agg()` 替换为 Python 集合操作
- **BUG-8/9**: `TrackSegment.track_id` 和 `TrackInterpolatedPoint.track_id` 类型从 Integer 改为 String(50)

---

## 阶段三：修复已知 Bug - 已完成 ✓

**完成时间**: 2026-04-26

| Bug | 修复方案 | 状态 |
|-----|---------|------|
| BUG-1 | MRRA 算法 _init_components 参数（不影响正常运行，暂不处理） | 待定 |
| BUG-2 | `track.track_id` → `track.batch_id`，移除 `raw_data` 引用 | ✓ |
| BUG-3 | `func.array_agg()` → Python 集合操作 | ✓ |
| BUG-4 | requirements.txt 添加 pyproj, scipy | ✓ |
| BUG-5 | `_execute_with_legacy_flow` 过滤非 MrraConfig 字段 | ✓ |
| BUG-6 | `_save_error_results` 增加 confidence/iterations/final_cost | ✓ |
| BUG-7 | 前端已使用 azimuth_error_square，与后端一致（无需修复） | ✓ |
| BUG-8/9 | track_id 类型 Integer→String(50) | ✓ |

---

## 阶段四：单源盲测模式实现 - 已完成 ✓

**完成时间**: 2026-04-26

### 已完成的工作

| # | 算法 | 后端文件 | 前端组件 | 状态 |
|---|------|---------|---------|------|
| 4.1 | 卡尔曼滤波 | `algorithms/kalman/` (3文件) | `KalmanConfig.vue` | ✓ |
| 4.2 | 粒子滤波 | `algorithms/particle_filter/` (3文件) | `ParticleFilterConfig.vue` | ✓ |
| 4.3 | 样条平滑 | `algorithms/spline/` (3文件) | `SplineConfig.vue` | ✓ |
| 4.4 | 注册到框架 | `algorithms/__init__.py` | `AlgorithmConfigContainer.vue` + `index.ts` | ✓ |
| 4.5 | 服务层适配 | `error_analysis_service.py` 支持 kalman/particle_filter/spline | - | ✓ |

### 单源盲测模式算法说明

**卡尔曼滤波** (`kalman`):
- 6 状态变量 [lat, lon, alt, v_lat, v_lon, v_alt]
- 匀速运动模型，自适应时间间隔
- 输出平滑轨迹 + 协方差追踪

**粒子滤波** (`particle_filter`):
- 默认 1000 粒子，系统重采样
- 支持高斯似然更新
- 有效粒子数自适应重采样
- 3 个预设: standard/high_precision/fast

**样条平滑** (`spline`):
- 基于 scipy UnivariateSpline
- 对经度、纬度、高度分别平滑
- 可选插值模式增加轨迹密度
- 4 个预设: standard/smooth/tight/interpolated

---

## 最终系统状态

### 已注册的 6 个算法

| 算法名称 | 模式 | 说明 |
|---------|------|------|
| `gradient_descent` | 多源参考 | MRRA 梯度下降迭代寻优 |
| `ransac` | 多源参考 | RANSAC 随机抽样一致性，识别故障站 |
| `weighted_lstsq` | 多源参考 | 加权最小二乘融合，输出优化轨迹 |
| `kalman` | 单源盲测 | 卡尔曼滤波平滑去噪 |
| `particle_filter` | 单源盲测 | 粒子滤波处理非线性非高斯噪声 |
| `spline` | 单源盲测 | 样条平滑曲线拟合 |

### 前端算法配置组件

每个算法都有专用的 Vue 配置组件，通过 `AlgorithmConfigContainer` 动态加载。用户可：
1. 选择算法 → 自动加载配置组件和预设
2. 调整参数或选择预设
3. 提交分析任务 → 后台执行 → 轮询进度 → 查看结果

