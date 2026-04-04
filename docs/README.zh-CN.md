# PRD Pilot 中文文档

[English README](../README.md)

## 项目定位

PRD Pilot 是一个面向产品经理的 AI 工作台，用来把模糊想法快速整理成：

- 一份可评审的 `Requirement Spec`
- 一份中文 `PRD` 初稿
- 一个可直接预览和下载的单文件 HTML Demo
- 一份原型说明
- 一份一致性检查结果与修复建议

核心链路：

`输入需求 -> 解析 Requirement Spec -> 生成 PRD / Demo / 原型说明 -> Demo 质量门禁 -> 一致性检查 -> 定点修改`

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
- Demo 规划 + HTML 生成
- 原型说明生成

### 3. Demo 质量门禁

生成 Demo 后会统一检查：

- HTML 是否完整
- 关键按钮是否存在
- 是否有交互信号
- 页面主线是否连通
- 是否覆盖结果/反馈状态

如果首轮结果不合格，系统会先尝试自动修复一次，再返回结构化错误。

### 4. 一致性检查 v2

检查范围包括：

- 页面覆盖
- 功能覆盖
- 流程连通
- 命名一致
- 原型一致
- 场景缺失

输出内容包括：

- `severity`
- `evidence`
- `issues`
- `repair_actions`

### 5. 定点修改

底部的定点修改区用于局部更新而不是整份重写，支持：

- 修改目标用户
- 新增页面
- 删除功能
- 调整布局
- 切换风格
- 强化数据展示
- 精简 PRD
- 梳理流程

每次修改都会返回：

- `change_summary`
- `changed_sections`
- `affected_pages`

### 6. 接入能力

v0.2 版本把下面两类能力纳入正式范围：

- `mcp/` 目录下的 MCP 服务
- `.claude/skills/prd-pilot/` 下的 Claude Code Skill

接入说明见 [integration.md](integration.md)。

## 页面说明

### 右上角：模型配置

支持在浏览器内配置：

- 模型平台
- 模型名称
- API Key
- Base URL
- Max Tokens（留空表示自动）

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

### 左下：Requirement Spec

这是整个系统的统一输入基线：

- PRD 基于它生成
- Demo 基于它生成
- 一致性检查基于它比对
- 定点修改也会先调整它

### 右侧：评审产出

包含四个标签页：

- `PRD`
- `Demo`
- `原型说明`
- `一致性检查`

### 底部：定点修改

用于局部更新，字段包括：

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

默认访问地址：

- 前端：`http://127.0.0.1:5173`
- 后端健康检查：`http://127.0.0.1:8000/api/health`

前端默认通过 `/api` 访问后端，开发环境下由 Vite 代理到 `http://127.0.0.1:8000`。如果需要，也可以通过 `VITE_API_BASE_URL` 覆盖。

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

`generate-demo` 与 `iterate-demo` 成功返回中新增：

- `demo_quality`
- `generation_meta`

失败时会返回结构化错误：

- `error_code`
- `stage`
- `retryable`
- `detail`

## 测试与 CI

当前仓库包含：

- 后端 `pytest`
  - `use_cases`
  - Demo 阶段错误返回
  - 一致性检查输出
- 前端 Playwright smoke 用例
  - 正常闭环
  - Demo 超时错误态
- GitHub Actions
  - 后端测试
  - 前端构建
  - 浏览器烟测

CI 使用确定性的 mock provider，不依赖真实模型服务。

## 示例案例

标准案例放在 [`prd-pilot/docs/examples/`](../prd-pilot/docs/examples/README.md)：

- [校园二手交易平台](../prd-pilot/docs/examples/campus-secondhand-marketplace.md)
- [AI 简历优化工具](../prd-pilot/docs/examples/ai-resume-optimizer.md)

## 当前边界

- 原型输出是 `HTML Demo + 原型说明`
- 不生成图片型原型图
- 不做持久化版本回滚
- 一致性检查以规则引擎为主，不是 AI 评分器
