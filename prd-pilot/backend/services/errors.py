"""Shared service-layer errors for PRD Pilot."""

from __future__ import annotations

from typing import Any, Dict, Optional


class WorkflowStageError(ValueError):
    """Structured workflow-stage failure that can be surfaced to the UI."""

    def __init__(
        self,
        error_code: str,
        stage: str,
        detail: str,
        retryable: bool = True,
        status_code: int = 500,
        generation_meta: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(detail)
        self.error_code = error_code
        self.stage = stage
        self.detail = detail
        self.retryable = retryable
        self.status_code = status_code
        self.generation_meta = generation_meta or {}

    def to_payload(self) -> Dict[str, Any]:
        payload = {
            "error_code": self.error_code,
            "stage": self.stage,
            "retryable": self.retryable,
            "detail": self.detail,
        }
        if self.generation_meta:
            payload["generation_meta"] = self.generation_meta
        return payload


class DemoGenerationError(WorkflowStageError):
    """Backward-compatible alias for demo-stage failures."""
