# PRD Pilot

> AI workspace for product managers to turn vague ideas into Requirement Specs, PRDs, demo-ready HTML prototypes, consistency reports, and targeted iteration plans.

[![Stars](https://img.shields.io/github/stars/156181679-dev/prd-pilot?style=flat&label=Stars)](https://github.com/156181679-dev/prd-pilot/stargazers)
[![Forks](https://img.shields.io/github/forks/156181679-dev/prd-pilot?style=flat&label=Forks)](https://github.com/156181679-dev/prd-pilot/network/members)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Last Commit](https://img.shields.io/github/last-commit/156181679-dev/prd-pilot/main?style=flat)](https://github.com/156181679-dev/prd-pilot/commits/main)

[中文文档](docs/README.zh-CN.md)

![PRD Pilot cover](docs/screenshots/readme-cover.png)

## Demo Flow

![PRD Pilot demo flow](docs/screenshots/prd-pilot-demo.gif)

## What It Solves

PRD Pilot is built for product managers, indie builders, and small teams that need to move from a vague idea to a reviewable solution quickly.

Most generators can output a PRD or a mockup, but the workflow usually breaks when:

- the PRD and demo drift apart
- key pages or flows go missing
- feedback turns into a full rewrite

PRD Pilot keeps one shared `Requirement Spec` through generation, validation, and iteration so the output stays aligned.

## Preview

| Requirement Spec | Demo Preview | Consistency Check |
| --- | --- | --- |
| ![Requirement Spec](docs/screenshots/requirement-spec.png) | ![Demo preview](docs/screenshots/demo-preview.png) | ![Consistency check](docs/screenshots/consistency-check.png) |

| PRD Draft | Targeted Iteration | Home Workspace |
| --- | --- | --- |
| ![PRD output](docs/screenshots/prd-output.png) | ![Targeted iteration](docs/screenshots/targeted-iteration.png) | ![Home overview](docs/screenshots/home-overview.png) |

## Core Workflow

```mermaid
flowchart LR
    A["Input idea"] --> B["Structure Requirement Spec"]
    B --> C["Generate PRD"]
    B --> D["Generate Demo plan + HTML"]
    B --> E["Generate Prototype Outline"]
    D --> F["Demo quality gate"]
    C --> G["Consistency Check"]
    E --> G
    F --> G
    G --> H["Targeted Iteration"]
    H --> B
```

## Key Features

### Shared Requirement Spec

PRD Pilot first structures user input into a single internal spec:

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

This spec becomes the source of truth for generation, checks, and iteration.

### PRD + Demo + Prototype Outline

- `PRD`: Chinese Markdown draft for review
- `Demo`: single-file HTML prototype for preview and download
- `Prototype Outline`: structure, flow, and validation goals

### Demo Quality Gate

The demo pipeline validates:

- HTML completeness
- key button presence
- interaction signals
- main page connectivity
- result and feedback state coverage

If quality fails, PRD Pilot attempts one repair pass before returning a structured error.

### Consistency Check v2

Built-in checks cover:

- page coverage
- feature coverage
- flow connectivity
- naming consistency
- prototype alignment
- scenario coverage

Reports include:

- severity
- evidence
- issue list
- repair actions that can be mapped into targeted iteration

### Targeted Iteration

Instead of regenerating everything, PRD Pilot supports scoped updates such as:

- add page
- modify user
- remove feature
- adjust layout
- change style
- improve data density
- simplify PRD
- clarify flow

Each iteration returns:

- `change_summary`
- `changed_sections`
- `affected_pages`

### External Integrations

PRD Pilot now officially includes:

- thin MCP service in [`mcp/`](mcp/README.md)
- Claude Code skill in [`.claude/skills/prd-pilot/SKILL.md`](.claude/skills/prd-pilot/SKILL.md)
- shared `use_cases` layer used by Web API, MCP, and tests

See [docs/integration.md](docs/integration.md) for setup details.

## Examples

Standard cases are included in [`prd-pilot/docs/examples/`](prd-pilot/docs/examples/README.md):

- [Campus Secondhand Marketplace](prd-pilot/docs/examples/campus-secondhand-marketplace.md)
- [AI Resume Optimizer](prd-pilot/docs/examples/ai-resume-optimizer.md)

## Quick Start

### 1. Clone and start the backend

```bash
git clone https://github.com/156181679-dev/prd-pilot.git
cd prd-pilot/prd-pilot/backend
pip install -r requirements.txt
copy .env.example .env
python main.py
```

Example `.env`:

```env
OPENAI_PROVIDER=deepseek
OPENAI_API_KEY=your_deepseek_api_key_here
OPENAI_BASE_URL=https://api.deepseek.com/v1
OPENAI_MODEL=deepseek-chat
OPENAI_MAX_TOKENS=0
APP_HOST=127.0.0.1
APP_PORT=8000
```

### 2. Start the frontend

```bash
cd ../frontend
npm install
npm run dev
```

The frontend reads `VITE_API_BASE_URL` if you want to override the default `/api` path. In local dev, Vite proxies `/api` to `http://127.0.0.1:8000`.

### 3. Open the app

- Frontend: [http://127.0.0.1:5173](http://127.0.0.1:5173)
- Backend health: [http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health)
- API docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## API

Base URL: `http://127.0.0.1:8000`

| Endpoint | Method | Description |
| --- | --- | --- |
| `/api/health` | GET | Health check |
| `/api/model-options` | GET | List available models |
| `/api/test-model-config` | POST | Test API key + model connection |
| `/api/structure-requirement` | POST | Generate Requirement Spec from brief |
| `/api/generate-prd` | POST | Generate PRD from Requirement Spec |
| `/api/generate-demo` | POST | Generate HTML Demo from Requirement Spec |
| `/api/check-consistency` | POST | Cross-check PRD + Demo against Spec |
| `/api/iterate-prd` | POST | Scoped PRD update |
| `/api/iterate-demo` | POST | Scoped Demo update |

`generate-demo` and `iterate-demo` return:

- `demo_quality`
- `generation_meta`

Structured demo-stage failures return:

- `error_code`
- `stage`
- `retryable`
- `detail`

## Tests and CI

The repository includes:

- backend `pytest` coverage for `use_cases`, structured demo errors, and consistency output
- Playwright smoke coverage for the web happy path and demo timeout path
- GitHub Actions workflow for backend tests, frontend build, and browser smoke tests

## Tech Stack

### Frontend

- Vue 3
- Vite
- Element Plus
- Tailwind CSS
- MarkdownIt
- VueUse
- Playwright

### Backend

- FastAPI
- OpenAI-compatible API client
- Pydantic
- Python Dotenv
- FastMCP / MCP
- Pytest

## Project Structure

```text
.
+-- prd-pilot/
|   +-- backend/
|   |   +-- main.py
|   |   +-- requirements.txt
|   |   +-- services/
|   |   |   +-- llm_service.py
|   |   |   +-- use_cases.py
|   |   |   +-- mock_llm_service.py
|   |   +-- tests/
|   +-- frontend/
|   |   +-- src/
|   |   |   +-- App.vue
|   |   +-- tests/e2e/
|   |   +-- package.json
|   |   +-- vite.config.js
+-- mcp/
+-- docs/
|   +-- README.zh-CN.md
|   +-- integration.md
|   +-- screenshots/
+-- .claude/skills/prd-pilot/
+-- .github/workflows/
+-- README.md
+-- CONTRIBUTING.md
+-- ROADMAP.md
+-- LICENSE
```

## Documentation

- [中文文档](docs/README.zh-CN.md)
- [Integration Guide](docs/integration.md)
- [Contributing Guide](CONTRIBUTING.md)
- [Roadmap](ROADMAP.md)

## Current Scope

- prototype output is `HTML Demo + Prototype Outline`
- consistency checks are rule-based, not AI-score-driven
- targeted iteration is scoped, but not yet a persistent version system
- no image-based prototype generation

## License

MIT
