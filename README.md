# PRD Pilot

> AI PRD and demo workspace for product managers.

[中文文档](docs/README.zh-CN.md)

PRD Pilot helps product managers turn vague product ideas into a shared `Requirement Spec`, a reviewable PRD, a demo-ready HTML prototype, and targeted iteration plans.

**Core loop**

`Idea -> Requirement Spec -> PRD / Demo / Prototype Outline -> Consistency Check -> Targeted Iteration`

## At a Glance

- Shared `Requirement Spec` as the single source of truth
- Chinese PRD draft + single-file HTML demo from the same spec
- Built-in consistency checks across PRD, demo, and prototype outline
- Targeted iteration with scoped change summaries
- In-browser model configuration for OpenAI-compatible APIs

## Preview

| Home | Requirement Spec |
| --- | --- |
| ![Home overview](docs/screenshots/home-overview.png) | ![Requirement Spec](docs/screenshots/requirement-spec.png) |

| PRD | Demo |
| --- | --- |
| ![PRD output](docs/screenshots/prd-output.png) | ![Demo preview](docs/screenshots/demo-preview.png) |

| Consistency Check | Targeted Iteration |
| --- | --- |
| ![Consistency check](docs/screenshots/consistency-check.png) | ![Targeted iteration](docs/screenshots/targeted-iteration.png) |

## Why It Exists

Many AI tools can generate something quickly, but the outputs often drift:

- the PRD says one thing
- the demo shows another thing
- the interaction flow breaks in review
- feedback forces a full rewrite instead of a scoped edit

PRD Pilot is built to solve that gap.

## Who It's For

- student product managers who need to prepare requirement reviews quickly
- indie developers who need to turn raw ideas into reviewable specs and demos
- small teams without dedicated design or frontend prototyping support

## Workflow

```mermaid
flowchart LR
    A[Input Idea] --> B[Structure Requirement Spec]
    B --> C[Generate PRD]
    B --> D[Generate Demo HTML]
    B --> E[Generate Prototype Outline]
    C --> F[Consistency Check]
    D --> F
    E --> F
    F --> G[Targeted Iteration]
    G --> B
```

## Core Features

### 1. Requirement Spec Layer

PRD Pilot first normalizes user input into a shared internal structure:

- `product_name`
- `product_type`
- `target_users`
- `user_pain_points`
- `core_scenarios`
- `key_features`
- `primary_pages`
- `user_flow`
- `style_preference`
- `constraints`
- `success_criteria`

This spec becomes the single source of truth for generation, checking, and iteration.

### 2. Generation

- `PRD`: Chinese Markdown draft for requirement review
- `Demo`: single-file HTML prototype for direct preview and download
- `Prototype Outline`: page structure, flow, and validation goals

### 3. Validation

Built-in consistency checks include:

- page coverage
- feature coverage
- flow connectivity
- naming consistency
- prototype alignment
- scenario coverage

### 4. Targeted Iteration

Instead of redoing everything, PRD Pilot supports scoped updates such as:

- add page
- modify user
- remove feature
- adjust layout
- change style
- improve data density
- simplify PRD
- clarify flow

Each iteration returns a short change summary.

## Model Configuration

PRD Pilot supports page-level model configuration. Users can open the top-right model dialog and provide:

- provider
- model name
- API key
- base URL
- max tokens (optional; blank means auto)

Built-in provider presets:

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

The UI stores this configuration only in the current browser. It is not written back to the server.

## Quick Start

### 1. Backend

```bash
cd prd-pilot/backend
pip install -r requirements.txt
copy .env.example .env
python main.py
```

Default example config:

```env
OPENAI_PROVIDER=deepseek
OPENAI_API_KEY=your_deepseek_api_key_here
OPENAI_BASE_URL=https://api.deepseek.com/v1
OPENAI_MODEL=deepseek-chat
OPENAI_MAX_TOKENS=0
APP_HOST=0.0.0.0
APP_PORT=8000
```

`OPENAI_MAX_TOKENS=0` means the backend will not explicitly pass `max_tokens` and will let the selected model use its available output limit.

### 2. Frontend

```bash
cd prd-pilot/frontend
npm install
npm run dev
```

### 3. Open in Browser

- Frontend: [http://localhost:5173](http://localhost:5173)
- Backend health: [http://localhost:8000/api/health](http://localhost:8000/api/health)

## API

- `GET /api/model-options`
- `POST /api/test-model-config`
- `POST /api/structure-requirement`
- `POST /api/generate-prd`
- `POST /api/generate-demo`
- `POST /api/check-consistency`
- `POST /api/iterate-prd`
- `POST /api/iterate-demo`
- `GET /api/health`
- `GET /api/test-llm`

## Tech Stack

### Frontend

- Vue 3
- Vite
- Element Plus
- Tailwind CSS
- MarkdownIt
- VueUse

### Backend

- FastAPI
- OpenAI-compatible API client
- Pydantic
- Python Dotenv

## Project Structure

```text
.
├─ prd-pilot/
│  ├─ backend/
│  │  ├─ main.py
│  │  ├─ requirements.txt
│  │  └─ services/
│  │     └─ llm_service.py
│  └─ frontend/
│     ├─ src/
│     │  └─ App.vue
│     ├─ package.json
│     └─ vite.config.js
├─ docs/
│  ├─ README.zh-CN.md
│  └─ screenshots/
├─ README.md
└─ LICENSE
```

## Current Scope

- prototype output is `HTML Demo + Prototype Outline`
- no image-based prototype generation yet
- no persistent version rollback yet
- consistency check v1 is rule-based, not AI-score-driven

## Docs

- Chinese guide: [docs/README.zh-CN.md](docs/README.zh-CN.md)

## License

MIT
