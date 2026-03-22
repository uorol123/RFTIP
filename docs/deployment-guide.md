# MRRA 集成到 RFTIP 部署说明

## 完成状态

### 后端状态

| 状态 | 说明 |
|------|------|
| ✅ 数据模型 | 5张表已定义并注册到 Base.metadata |
| ✅ API模式 | Pydantic 模型已定义 |
| ✅ 算法模块 | MRRA 核心算法已迁移并适配 RFTIP |
| ✅ 服务层 | ErrorAnalysisService 已实现 |
| ✅ API路由 | 8个端点已注册 |
| ✅ 路由注册 | main.py 已更新 |
| ✅ 依赖安装 | pyproj, numpy, scipy 已安装 |

### 前端状态

| 状态 | 说明 |
|------|------|
| ✅ 类型定义 | errorAnalysis.ts 已创建 |
| ✅ API客户端 | errorAnalysis.ts 已创建 |
| ✅ 状态管理 | Pinia store 已创建 |
| ✅ 主页面 | ErrorAnalysis.vue 已创建 |
| ✅ 组件 | 5个组件已创建 |
| ✅ 路由配置 | /error-analysis 路由已添加 |
| ✅ 导航菜单 | "误差分析"链接已添加 |
| ✅ 依赖 | echarts, vue-echarts 已安装 |
| ✅ 构建验证 | 构建成功 |

---

## API 端点列表

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/error-analysis/analyze` | POST | 创建分析任务 |
| `/api/error-analysis/config` | GET | 获取默认配置 |
| `/api/error-analysis/tasks` | GET | 获取任务列表 |
| `/api/error-analysis/tasks/{id}` | GET | 获取任务详情 |
| `/api/error-analysis/tasks/{id}/results` | GET | 获取分析结果 |
| `/api/error-analysis/tasks/{id}/segments` | GET | 获取航迹段 |
| `/api/error-analysis/tasks/{id}/matches` | GET | 获取匹配组 |
| `/api/error-analysis/tasks/{id}/chart` | GET | 获取图表数据 |

---

## 启动步骤

### 1. 启动后端

```bash
cd D:\myworld\毕设\RFTIP\backend
python main.py
```

后端将在 http://localhost:8000 启动

### 2. 启动前端

```bash
cd D:\myworld\毕设\RFTIP\frontend
npm run dev
```

前端将在 http://localhost:5173 启动

### 3. 访问误差分析页面

在浏览器中访问：
```
http://localhost:5173/error-analysis
```

---

## 使用流程

1. **选择数据文件**
   - 从下拉框选择已上传的轨迹数据文件

2. **配置分析参数**
   - 网格分辨率（默认 0.2 度）
   - 时间窗口（默认 60 秒）
   - 匹配距离阈值（默认 0.12 度）
   - 最小航迹点数（默认 10）
   - 代价函数权重

3. **启动分析**
   - 点击"开始分析"按钮
   - 查看实时进度
   - 等待分析完成

4. **查看结果**
   - 切换到"图表"标签页查看可视化
   - 切换到"表格"标签页查看详细数据
   - 切换到"匹配组"标签页查看匹配信息

5. **导出结果**
   - 点击"导出报告"生成 PDF/JSON
   - 点击"导出CSV"下载原始数据

---

## 数据库表结构

### error_analysis_tasks
误差分析任务主表

### track_segments
航迹段数据（从原始轨迹提取的关键段）

### match_groups
航迹匹配组（多雷达航迹点匹配结果）

### error_results
雷达误差计算结果（方位角、距离、俯仰角）

### track_interpolated_points
插值点数据（时间插值后的航迹点）

---

## 注意事项

1. **雷达站位置配置**
   - 确保 `radar_stations` 表中配置了雷达站位置信息（经度、纬度、高度）
   - 误差计算需要雷达站位置作为参考点

2. **数据要求**
   - `data_files` 表中需要有已处理的轨迹数据
   - `flight_tracks_raw` 表中需要有原始航迹点数据

3. **性能考虑**
   - 大数据量分析可能需要较长时间（建议使用后台任务）
   - 可以调整配置参数来平衡精度和速度

4. **类型检查问题**
   - 前端现有文件有一些类型错误（不影响功能）
   - 使用 `npm run build-only` 跳过类型检查进行构建

---

## 故障排除

### 问题1: 后端启动失败

```
ModuleNotFoundError: No module named 'xxx'
```

**解决方法**:
```bash
pip install xxx
```

### 问题2: 数据库表未创建

**解决方法**:
```bash
cd backend
python -c "from core.database import Base, engine; import app.models; Base.metadata.create_all(bind=engine); print('Tables created')"
```

### 问题3: API 返回 404

**解决方法**:
- 确认 main.py 中已添加 error_analysis 路由
- 确认路由路径正确：`/api/error-analysis/...`

### 问题4: 前端构建类型错误

**解决方法**:
- 使用 `npm run build-only` 跳过类型检查
- 或修复现有文件的类型错误

---

## 文件清单

### 后端新增文件

```
backend/app/
├── models/
│   └── error_analysis.py
├── schemas/
│   └── error_analysis.py
├── utils/mrra/
│   ├── __init__.py
│   ├── config.py
│   ├── track_extractor.py
│   ├── track_interpolator.py
│   ├── track_matcher.py
│   └── error_calculator.py
├── services/
│   └── error_analysis_service.py
└── routers/
    └── error_analysis.py
```

### 前端新增文件

```
frontend/src/
├── types/
│   └── errorAnalysis.ts
├── api/
│   └── errorAnalysis.ts
├── stores/
│   └── errorAnalysis.ts
├── views/
│   └── ErrorAnalysis.vue
└── components/errorAnalysis/
    ├── ErrorConfigPanel.vue
    ├── ErrorProgressBar.vue
    ├── ErrorResultChart.vue
    ├── ErrorTable.vue
    └── MatchVisualization.vue
```

---

## 版本信息

- **文档版本**: v1.0
- **创建时间**: 2025-03-22
- **RFTIP 版本**: v1.0.0
- **Python 版本**: 3.9+
- **Node.js 版本**: ^20.19.0 || >=22.12.0
