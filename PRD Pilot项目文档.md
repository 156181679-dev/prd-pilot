# PRD Pilot 项目文档

## 项目定位

PRD Pilot 是一个面向产品经理的 AI PRD 与 Demo 快速生成工作台。

它面向缺乏设计或前端资源、但需要快速完成需求评审与演示的学生 PM 与独立开发者，帮助用户把模糊需求快速整理成：

- 一份可评审的 `Requirement Spec`
- 一份中文 PRD 初稿
- 一个可演示的单文件 HTML Demo
- 一份原型说明
- 一份一致性检查结果与修复建议

## 主链路

1. 输入需求
2. 解析 Requirement Spec
3. 基于同一份摘要生成 PRD / Demo / 原型说明
4. 运行一致性检查
5. 根据问题做定点修改
6. 查看本轮变更摘要

## 当前功能

### 1. 结构化需求层

- 快速模式输入
- 结构化模式输入
- 页面右上角弹出式模型配置
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

## API 说明

| 方法 | 路径 | 说明 |
|------|------|------|
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

## 技术实现

### 前端

- Vue 3
- Vite
- Element Plus
- Tailwind CSS
- MarkdownIt
- VueUse

### 后端

- FastAPI
- OpenAI Compatible API
- DeepSeek `deepseek-chat`
- Python Dotenv

## 运行方式

### 后端

```bash
cd prd-pilot/backend
pip install -r requirements.txt
python main.py
```

### 前端

```bash
cd prd-pilot/frontend
npm install
npm run dev
```

## 配置说明

`.env` 默认按 DeepSeek 配置：

```env
OPENAI_PROVIDER=deepseek
OPENAI_API_KEY=your_deepseek_api_key_here
OPENAI_BASE_URL=https://api.deepseek.com/v1
OPENAI_MODEL=deepseek-chat
OPENAI_MAX_TOKENS=0
```

仓库默认不包含真实 `.env`，请从 `.env.example` 自行复制。

页面右上角的“配置模型”按钮支持直接填写：

- 模型平台
- 模型名称
- API Key
- Base URL
- Max Tokens

其中 `Max Tokens` 留空时，会按当前模型最大可用输出上限处理。

内置平台包括：

- `DeepSeek`
- `OpenAI`
- `OpenRouter`
- `Zhipu / GLM`
- `SiliconFlow`
- `Moonshot`
- `Groq`
- `DashScope / Qwen`
- `Ollama (Local)`
- `Custom OpenAI Compatible`

## 当前边界

- 原型输出为 `HTML Demo + 原型说明`
- 不生成图片型原型图
- 不做持久化版本回滚
- 一致性检查首版以规则引擎为主

## 建议展示素材

- 案例 1：校园二手交易平台
- 案例 2：AI 简历优化工具
- 录屏：从输入需求到一致性修复的完整闭环



