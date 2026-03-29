"""Thin MCP adapter for PRD Pilot."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT_DIR / "prd-pilot" / "backend"
SCRIPT_DIR = Path(__file__).resolve().parent

for path in (str(SCRIPT_DIR), str(ROOT_DIR)):
    if path in sys.path:
        sys.path.remove(path)

from fastmcp import FastMCP

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

load_dotenv(BACKEND_DIR / ".env")

from services.use_cases import PRDPilotUseCases  # noqa: E402


mcp = FastMCP(
    name="PRD Pilot MCP",
    instructions=(
        "Use PRD Pilot as a PM-focused workflow: structure requirement -> generate PRD/demo "
        "-> consistency check -> targeted iteration."
    ),
    version="0.1.0",
)

_use_cases = PRDPilotUseCases()


@mcp.tool()
async def structure_requirement(brief: Dict[str, Any], model_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Structure a raw brief into the shared Requirement Spec."""
    return await _use_cases.structure_requirement(brief, model_config=model_config)


@mcp.tool()
async def generate_prd(
    brief: Optional[Dict[str, Any]] = None,
    requirement_spec: Optional[Dict[str, Any]] = None,
    model_config: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Generate a Chinese PRD draft from a brief or Requirement Spec."""
    return await _use_cases.generate_prd(
        brief=brief,
        requirement_spec=requirement_spec,
        model_config=model_config,
    )


@mcp.tool()
async def generate_demo(
    brief: Optional[Dict[str, Any]] = None,
    requirement_spec: Optional[Dict[str, Any]] = None,
    prd_content: Optional[str] = None,
    model_config: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Generate a single-file HTML demo and prototype outline."""
    return await _use_cases.generate_demo(
        brief=brief,
        requirement_spec=requirement_spec,
        prd_content=prd_content,
        model_config=model_config,
    )


@mcp.tool()
async def check_consistency(
    requirement_spec: Dict[str, Any],
    prd: str = "",
    demo_html: str = "",
    prototype_outline: str = "",
) -> Dict[str, Any]:
    """Check PRD/demo alignment with rule-based consistency checks."""
    return await _use_cases.check_consistency(
        requirement_spec=requirement_spec,
        prd=prd,
        demo_html=demo_html,
        prototype_outline=prototype_outline,
    )


@mcp.tool()
async def iterate_prd(
    brief: Optional[Dict[str, Any]] = None,
    requirement_spec: Optional[Dict[str, Any]] = None,
    current_prd: str = "",
    change_type: str = "",
    target_module: str = "prd",
    affected_pages: Optional[List[str]] = None,
    instruction: str = "",
    model_config: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Apply a targeted PRD change and return the revised PRD plus change metadata."""
    return await _use_cases.iterate_prd(
        brief=brief,
        requirement_spec=requirement_spec,
        current_prd=current_prd,
        change_type=change_type,
        target_module=target_module,
        affected_pages=affected_pages,
        instruction=instruction,
        model_config=model_config,
    )


@mcp.tool()
async def iterate_demo(
    brief: Optional[Dict[str, Any]] = None,
    requirement_spec: Optional[Dict[str, Any]] = None,
    current_demo_html: str = "",
    current_prd: Optional[str] = None,
    change_type: str = "",
    target_module: str = "demo",
    affected_pages: Optional[List[str]] = None,
    instruction: str = "",
    model_config: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Apply a targeted demo change and return the revised HTML plus change metadata."""
    return await _use_cases.iterate_demo(
        brief=brief,
        requirement_spec=requirement_spec,
        current_demo_html=current_demo_html,
        current_prd=current_prd,
        change_type=change_type,
        target_module=target_module,
        affected_pages=affected_pages,
        instruction=instruction,
        model_config=model_config,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the PRD Pilot MCP server.")
    parser.add_argument("--transport", choices=["stdio", "sse", "streamable-http"], default="stdio")
    parser.add_argument("--host", default=os.getenv("MCP_HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.getenv("MCP_PORT", "8765")))
    args = parser.parse_args()

    if args.transport == "stdio":
        mcp.run()
        return

    if args.transport == "sse":
        mcp.run_sse_async(host=args.host, port=args.port)
        return

    mcp.run_streamable_http_async(host=args.host, port=args.port)


if __name__ == "__main__":
    main()
