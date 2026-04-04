# PRD Pilot Roadmap

> Last updated: 2026-04-04

This document outlines the planned direction for PRD Pilot. Features are organized by priority level. Items with 🔴 are planned for the next release, 🟡 are in discussion, and 🟢 are nice-to-have.

---

## 🔴 Next Release (v0.5)

### Online Demo / Try-It-Now
- [ ] **Static HTML demo page** — browser-based interactive walkthrough, no install required
- [ ] **One-click deploy buttons** — Vercel / Railway / Replit for instant setup
- [ ] **Colab notebook** — Google Colab version for zero-setup experimentation

### LLM Provider Expansion
- [ ] **Claude via OpenRouter** — expose as explicit preset (backend already supports via OpenRouter)
- [ ] **Gemini 2.0 / 2.5** via Google AI Studio — add as dedicated provider
- [ ] **Azure OpenAI** — enterprise support

### Export Formats
- [ ] **PDF export for PRD** — generate a styled PDF from the Markdown output
- [ ] **Jira-compatible format** — export requirements as Jira tickets
- [ ] **Figma / FigJam outline** — structured text export for copy-paste into Figma

---

## 🟡 Planned (v0.6–v1.0)

### Consistency Check v2
- [ ] **AI-scored consistency** — replace rule-based checks with a dedicated LLM prompt that scores alignment 0–100 and explains gaps
- [ ] **Gap report** — human-readable explanation of every inconsistency, not just a list
- [ ] **Auto-fix suggestions** — LLM proposes how to resolve each inconsistency

### Iteration Improvements
- [ ] **Visual diff** — show before/after at the page level, not just text diff
- [ ] **Iteration history** — version rollback for Requirement Spec, PRD, and Demo
- [ ] **Branch-based iteration** — try an experimental direction without overwriting the main spec

### Multi-User / Team Features
- [ ] **API key management UI** — per-user API key storage
- [ ] **Project history** — save and reload past requirement sessions
- [ ] **Share link** — generate a read-only link to a Requirement Spec review

### Documentation
- [ ] **Full English UI** — internationalization support for the Vue frontend
- [ ] **Prompts documentation** — document what each LLM prompt does (for power users who want to customize)
- [ ] **Video demo** — 2-minute walkthrough showing the consistency check in action

---

## 🟢 Future Ideas

These are ideas worth exploring but not yet scheduled:

- **Image-based prototype generation** — upload a sketch, get an HTML prototype
- **Collaborative editing** — real-time multi-user spec editing
- **PRD review mode** — structured feedback workflow for stakeholders
- **Native Figma plugin** — bidirectional sync with Figma
- **Test case generation** — auto-generate test cases from the Requirement Spec
- **AI agent integration** — plug into existing PM tools (Notion, Linear, Confluence)

---

## Shipped History

### v0.4 (2026-03-27)
- Initial public release
- Shared Requirement Spec as source of truth
- PRD + Demo + Prototype Outline generation
- 6-rule consistency checking
- Scoped iteration (add page, modify user, etc.)
- Multi-provider LLM support (DeepSeek, OpenAI, OpenRouter, Zhipu, Moonshot, Groq, Ollama)
- Vue 3 + FastAPI tech stack

---

## How to Influence the Roadmap

- ⭐ Star the project to show demand
- 🐛 Report bugs and missing features as GitHub Issues
- 💬 Join discussions — your use case might change what we prioritize next
- 🔀 Pull requests are always welcome, especially for `Next Release` items

---

*This roadmap is a living document. Priorities shift based on user feedback. Last shipped features don't guarantee future availability.*
