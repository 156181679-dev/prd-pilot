# PRD Pilot MCP

This directory contains the thin MCP adapter for PRD Pilot.

## What it exposes

- `structure_requirement`
- `generate_prd`
- `generate_demo`
- `check_consistency`
- `iterate_prd`
- `iterate_demo`

## Run locally

Default transport is stdio:

```bash
cd prd-pilot
python ..\mcp\mcp_service.py
```

Optional streamable HTTP mode:

```bash
python ..\mcp\mcp_service.py --transport streamable-http --host 127.0.0.1 --port 8765
```

## Client mapping

Use the same shared workflow in every client:

1. Structure the requirement.
2. Generate PRD and/or demo.
3. Run consistency checks.
4. Apply targeted iteration.
