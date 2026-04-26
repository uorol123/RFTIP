# 误差分析模块架构完善计划

## 目标
完善 RFTIP 项目的误差分析模块，支持多算法扩展架构。

## 架构概览

### 已实现部分
- 算法基类 `BaseErrorAnalysisAlgorithm`
- 算法工厂 `AlgorithmFactory`
- 算法注册表 `registry`
- MRRA 算法适配器 `MrraAlgorithm`
- 前端算法选择器 `AlgorithmSelector`
- 算法管理 API 端点

### 需要完善的部分

## 后端任务

### 1. 数据库模型更新
- [ ] 添加 `algorithm_name` 字段到 `ErrorAnalysisTask` 模型
- [ ] 创建数据库迁移脚本

### 2. 服务层更新
- [ ] 修改 `create_analysis_task` 方法添加算法名称参数
- [ ] 在 `execute_analysis` 方法中使用 `AlgorithmFactory` 创建算法实例
- [ ] 更新 API 请求模型 `ErrorAnalysisRequest` 添加 `algorithm` 字段

### 3. API 路由更新
- [ ] 更新 `/analyze` 端点支持算法选择
- [ ] 更新响应类型

## 前端任务

### 1. 创建算法配置目录结构
```
frontend/src/components/errorAnalysis/algorithms/
├── index.ts
├── AlgorithmConfigContainer.vue
├── gradient_descent/
│   └── GradientDescentConfig.vue
└── AlgorithmConfigBase.vue
```

### 2. 创建 GradientDescentConfig.vue
- 数据选择（雷达站、轨迹）
- 预设配置选择
- 参数配置表单

### 3. 创建 AlgorithmConfigContainer.vue
- 动态加载算法配置组件
- 管理算法切换状态

### 4. 更新 ErrorConfigPanel.vue
- 使用新的 AlgorithmConfigContainer 组件

## TDD 原则
1. 先写测试
2. 运行测试（失败）
3. 编写最小实现
4. 运行测试（通过）
5. 重构
6. 确保覆盖率 80%+

## 优先级
1. 后端数据模型和迁移（高优先级）
2. 后端服务层更新（高优先级）
3. 前端算法配置组件（中优先级）
4. 集成测试（高优先级）
