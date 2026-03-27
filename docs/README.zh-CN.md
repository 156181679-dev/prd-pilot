# PRD Pilot 中文文档

[English README](../README.md)

## 项目定位

PRD Pilot 是一个面向产品经理的 AI PRD 与 Demo 工作台，用来把模糊想法快速整理成：

- 一份可评审的 `Requirement Spec`
- 一份中文 PRD 初稿
- 一个可演示的单文件 HTML Demo
- 一份原型说明
- 一份一致性检查结果与修复建议

核心链路：

`输入需求 -> 解析 Requirement Spec -> 生成 PRD / Demo / 原型说明 -> 一致性检查 -> 定点修改`

## 适用对象

- 学生产品经理
- 独立开发者
- 缺乏设计或前端原型资源的小团队

## 核心能力

### 1. 结构化需求层

- 快速模式输入
- 结构化模式输入
- Requirement Spec 自动抽取
- Requirement Spec 前端可编辑

### 2. 生成能力

- PRD 生成
- Demo HTML 生成
- 原型说明生成

### 3. 验证能力

- 页面覆盖检查
- 功能覆盖检查
- 流程连通检查
- 命名一致检查
- 原型一致检查
- 场景缺失检查

### 4. 迭代能力

- 结构化编辑指令
- 定点更新 PRD
- 定点更新 Demo
- 返回 `change_summary`、`changed_sections`、`affected_pages`

## 页面说明

### 右上角：配置模型

- 选择模型平台
- 选择或填写模型名称
- 填写 API Key
- 填写 Base URL
- 可选填写 Max Tokens，留空时默认按模型可用上限处理

当前内置平台：

- DeepSeek
- OpenAI
- OpenRouter
- Zhipu / GLM
- SiliconFlow
- Moonshot
- Groq
- DashScope / Qwen
- Ollama (Local)
- Custom OpenAI Compatible

### 左侧：需求输入

支持两种模式：

- 快速模式：适合一句模糊想法直接进入流程
- 结构化模式：适合已经有较完整需求信息时增强输入质量

### 左下：需求摘要 / Requirement Spec

这是整个系统的输入基线：

- PRD 基于它生成
- Demo 基于它生成
- 一致性检查基于它比对
- 定点修改也会先改它

### 右侧：评审产出

包含 4 个标签：

- `PRD`
- `Demo`
- `原型说明`
- `一致性检查`

### 底部：定点修改

用于局部修改而不是整份重写，核心字段包括：

- 修改类型
- 目标模块
- 影响页面
- 修改说明

## 推荐使用流程

1. 输入需求
2. 点击 `解析需求摘要`
3. 检查 Requirement Spec 是否合理
4. 生成 PRD
5. 生成 Demo 与原型说明
6. 运行一致性检查
7. 根据问题做定点修改

## 启动方式

### 后端

```bash
cd prd-pilot/backend
pip install -r requirements.txt
copy .env.example .env
python main.py
```

### 前端

```bash
cd prd-pilot/frontend
npm install
npm run dev
```

访问地址：

- 前端：`http://localhost:5173`
- 后端健康检查：`http://localhost:8000/api/health`

## API

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/api/model-options` | 返回内置模型平台、推荐模型和默认配置 |
| POST | `/api/test-model-config` | 测试页面内填写的模型配置是否可用 |
| POST | `/api/structure-requirement` | 从 brief 解析 Requirement Spec |
| POST | `/api/generate-prd` | 基于 Requirement Spec 生成 PRD |
| POST | `/api/generate-demo` | 基于 Requirement Spec 生成 Demo 与原型说明 |
| POST | `/api/check-consistency` | 检查 PRD / Demo / 原型说明的一致性 |
| POST | `/api/iterate-prd` | 根据结构化编辑指令更新 PRD |
| POST | `/api/iterate-demo` | 根据结构化编辑指令更新 Demo |
| GET | `/api/health` | 健康检查 |
| GET | `/api/test-llm` | 测试模型连接 |

## 当前边界

- 原型输出为 `HTML Demo + 原型说明`
- 不生成图片型原型图
- 不做持久化版本回滚
- 一致性检查首版以规则引擎为主
