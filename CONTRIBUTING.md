# Contributing to PRD Pilot

Thank you for your interest in contributing! PRD Pilot is an open, work-in-progress project and contributions are welcome.

---

## How to Contribute

### Reporting Issues

- Use [GitHub Issues](https://github.com/156181679-dev/prd-pilot/issues) to report bugs or suggest features
- For bugs, please include:
  - What you expected to happen
  - What actually happened
  - Steps to reproduce
  - Your OS, Python version, Node.js version
- Search existing issues before creating a new one

### Submitting Code Changes

1. **Fork the repository**
2. **Create a branch** for your change:
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```
3. **Make your changes** — keep commits small and focused
4. **Test locally** (see Development Setup below)
5. **Commit with a clear message**:
   ```bash
   git commit -m "Add: support for Claude via OpenRouter"
   ```
6. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```
7. **Open a Pull Request** against `main`

---

## Development Setup

### Prerequisites

- Python 3.10+
- Node.js 18+
- An OpenAI-compatible API key (DeepSeek, OpenAI, OpenRouter, etc.)

### Backend

```bash
cd prd-pilot/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API key

# Run
python main.py
```

Backend runs at `http://localhost:8000`. API docs at `http://localhost:8000/docs`.

### Frontend

```bash
cd prd-pilot/frontend

# Install dependencies
npm install

# Run dev server (backend must be running separately)
npm run dev
```

Frontend runs at `http://localhost:5173`.

### Running Tests

```bash
# Backend tests (if any)
cd backend
pytest  # or python -m pytest

# Frontend type check
cd frontend
npm run type-check
```

---

## Code Conventions

### Python (Backend)

- Use type hints where possible
- Follow PEP 8
- Pydantic models for all API request/response schemas
- Async/await for all LLM and I/O operations

### JavaScript / Vue (Frontend)

- Vue 3 Composition API (`<script setup>`)
- Element Plus components for UI
- Tailwind CSS for styling
- No mixing of Options API and Composition API in the same file

### Commit Message Format

```
<type>: <short description>

[optional body explaining what and why]
```

Types: `Add`, `Fix`, `Refactor`, `Docs`, `Style`, `Test`, `Chore`

Examples:
```
Add: support Gemini 2.5 Flash via OpenRouter
Fix: consistency check missing flow coverage
Docs: add OpenRouter setup to README
Refactor: extract LLM prompts into separate module
```

---

## Areas to Contribute

High-value contributions right now:

- [ ] **New LLM provider support** — add support for more OpenAI-compatible APIs
- [ ] **Export formats** — PDF export for PRD, Figma-compatible format for prototypes
- [ ] **Test case generation** — auto-generate test cases from Requirement Spec
- [ ] **Consistency check v2** — AI-scored consistency instead of rule-based
- [ ] **Localization** — English UI labels and prompts
- [ ] **API authentication** — add API key management for multi-user deployments
- [ ] **Demo deployment** — one-click deploy to Vercel / Railway

See [ROADMAP.md](ROADMAP.md) for the full planned feature list.

---

## Code of Conduct

Be respectful and constructive. Disagreements are fine; disrespect is not.

---

## Questions?

Open a GitHub Discussion or reach out via the project page.
