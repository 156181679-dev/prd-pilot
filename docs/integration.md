# Integration Guide

PRD Pilot exposes a thin integration surface so external tools can reuse the same workflow as the web app.

## Shared workflow

1. Structure the requirement.
2. Generate PRD and/or demo.
3. Run consistency checks.
4. Apply targeted iteration.

## 1) Cursor

If your Cursor configuration supports an MCP server definition, point it to the local MCP entrypoint from the repository root:

```json
{
  "mcpServers": {
    "prd-pilot": {
      "command": "python",
      "args": ["mcp/mcp_service.py"],
      "cwd": "/path/to/prd-pilot-repo"
    }
  }
}
```

If you prefer a networked transport, start the server with:

```bash
python mcp/mcp_service.py --transport streamable-http --host 127.0.0.1 --port 8765
```

## 2) Cherry Studio

Cherry Studio can connect to the same MCP server using the same tool list.

Recommended local command from the repository root:

```bash
python mcp/mcp_service.py
```

If your client only accepts a URL-style transport, use streamable HTTP mode and point the client to `http://127.0.0.1:8765`.

## 3) Claude Code

This repository already includes a Claude Code skill at:

```text
.claude/skills/prd-pilot/SKILL.md
```

Use it when you want Claude Code to follow the PRD Pilot workflow directly:

- structure requirement
- generate PRD / demo
- check consistency
- targeted iteration

## Minimal backend startup

```bash
cd prd-pilot/backend
pip install -r requirements.txt
copy .env.example .env
python main.py
```

## Tool mapping

- `structure_requirement`
- `generate_prd`
- `generate_demo`
- `check_consistency`
- `iterate_prd`
- `iterate_demo`
