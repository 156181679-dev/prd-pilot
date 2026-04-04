"""Thin application use-cases for PRD Pilot."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .llm_service import get_llm_service, get_model_options


class PRDPilotUseCases:
    """Reusable application boundary shared by Web API and MCP tools."""

    def __init__(self, llm_service=None):
        self.llm_service = llm_service or get_llm_service()

    @staticmethod
    def _to_dict(value: Any) -> Dict[str, Any]:
        if value is None:
            return {}
        if isinstance(value, dict):
            return dict(value)
        if hasattr(value, "model_dump"):
            return value.model_dump()
        return dict(value)

    @classmethod
    def serialize_brief(cls, brief: Any) -> Dict[str, Any]:
        return cls._to_dict(brief)

    @classmethod
    def serialize_requirement_spec(cls, requirement_spec: Any) -> Dict[str, Any]:
        return cls._to_dict(requirement_spec)

    @classmethod
    def serialize_model_config(cls, model_config: Any) -> Optional[Dict[str, Any]]:
        if model_config is None:
            return None
        return cls._to_dict(model_config)

    @staticmethod
    def validate_brief(brief: Any) -> None:
        brief_dict = PRDPilotUseCases.serialize_brief(brief)
        required_fields = [
            brief_dict.get("product_name"),
            brief_dict.get("problem_statement"),
            brief_dict.get("target_users"),
            brief_dict.get("user_pain_points"),
            brief_dict.get("key_scenarios"),
            brief_dict.get("core_features"),
        ]
        if not any(str(value or "").strip() for value in required_fields):
            raise ValueError(
                "请至少填写需求描述、产品名称、目标用户、用户痛点、核心场景或核心功能中的一项。"
            )

    async def resolve_requirement_spec(
        self,
        brief: Any = None,
        requirement_spec: Any = None,
        model_config: Any = None,
    ) -> Dict[str, Any]:
        if requirement_spec:
            return self.serialize_requirement_spec(requirement_spec)
        if not brief:
            raise ValueError("缺少 brief 或 requirement_spec，无法继续处理。")
        self.validate_brief(brief)
        return await self.llm_service.structure_requirement(
            self.serialize_brief(brief),
            model_config=self.serialize_model_config(model_config),
        )

    def get_model_options(self) -> Dict[str, Any]:
        return get_model_options()

    def test_model_config(self, model_config: Any = None) -> Dict[str, Any]:
        return self.llm_service.test_model_config(self.serialize_model_config(model_config))

    async def structure_requirement(self, brief: Any, model_config: Any = None) -> Dict[str, Any]:
        self.validate_brief(brief)
        requirement_spec = await self.llm_service.structure_requirement(
            self.serialize_brief(brief),
            model_config=self.serialize_model_config(model_config),
        )
        return {
            "requirement_spec": requirement_spec,
            "brief": self.serialize_brief(brief),
        }

    async def generate_prd(
        self,
        brief: Any = None,
        requirement_spec: Any = None,
        model_config: Any = None,
    ) -> Dict[str, Any]:
        resolved_requirement_spec = await self.resolve_requirement_spec(
            brief=brief,
            requirement_spec=requirement_spec,
            model_config=model_config,
        )
        prd_content = await self.llm_service.generate_prd(
            resolved_requirement_spec,
            model_config=self.serialize_model_config(model_config),
        )
        return {
            "prd": prd_content,
            "requirement_spec": resolved_requirement_spec,
            "brief": self.serialize_brief(brief) if brief else None,
        }

    async def generate_demo(
        self,
        brief: Any = None,
        requirement_spec: Any = None,
        prd_content: Optional[str] = None,
        model_config: Any = None,
    ) -> Dict[str, Any]:
        resolved_requirement_spec = await self.resolve_requirement_spec(
            brief=brief,
            requirement_spec=requirement_spec,
            model_config=model_config,
        )
        demo_bundle = await self.llm_service.generate_demo_html(
            requirement_spec=resolved_requirement_spec,
            prd_content=prd_content,
            model_config=self.serialize_model_config(model_config),
        )
        prototype_outline = await self.llm_service.generate_prototype_outline(
            requirement_spec=resolved_requirement_spec,
            prd_content=prd_content,
            demo_html=demo_bundle["demo_html"],
            demo_plan=demo_bundle.get("demo_plan"),
            model_config=self.serialize_model_config(model_config),
        )
        generation_meta = dict(demo_bundle.get("generation_meta") or {})
        phases_completed = list(generation_meta.get("phases_completed") or [])
        if "prototype_outline" not in phases_completed:
            phases_completed.append("prototype_outline")
        generation_meta["phases_completed"] = phases_completed
        return {
            "demo_html": demo_bundle["demo_html"],
            "prototype_outline": prototype_outline,
            "demo_quality": demo_bundle.get("demo_quality"),
            "generation_meta": generation_meta,
            "requirement_spec": resolved_requirement_spec,
            "brief": self.serialize_brief(brief) if brief else None,
        }

    async def check_consistency(
        self,
        requirement_spec: Any,
        prd: str = "",
        demo_html: str = "",
        prototype_outline: str = "",
    ) -> Dict[str, Any]:
        if not str(prd or "").strip() and not str(demo_html or "").strip():
            raise ValueError("请至少提供 PRD 或 Demo 内容用于一致性检查。")
        return self.llm_service.check_consistency(
            requirement_spec=self.serialize_requirement_spec(requirement_spec),
            prd=prd,
            demo_html=demo_html,
            prototype_outline=prototype_outline,
        )

    async def iterate_prd(
        self,
        brief: Any = None,
        requirement_spec: Any = None,
        current_prd: str = "",
        change_type: str = "",
        target_module: str = "prd",
        affected_pages: Optional[List[str]] = None,
        instruction: str = "",
        model_config: Any = None,
    ) -> Dict[str, Any]:
        if not str(instruction or "").strip():
            raise ValueError("请填写本次修改说明。")
        if not str(current_prd or "").strip():
            raise ValueError("当前 PRD 内容不能为空。")
        resolved_requirement_spec = await self.resolve_requirement_spec(
            brief=brief,
            requirement_spec=requirement_spec,
            model_config=model_config,
        )
        change_request = {
            "change_type": change_type,
            "target_module": target_module or "prd",
            "affected_pages": affected_pages or [],
            "instruction": instruction,
        }
        revised_requirement_spec = await self.llm_service.revise_requirement_spec(
            resolved_requirement_spec,
            change_request,
            model_config=self.serialize_model_config(model_config),
        )
        prd_content = await self.llm_service.iterate_prd(
            requirement_spec=revised_requirement_spec,
            current_prd=current_prd,
            change_request=change_request,
            model_config=self.serialize_model_config(model_config),
        )
        change_meta = self.llm_service.build_change_metadata(change_request, revised_requirement_spec)
        return {
            "prd": prd_content,
            "requirement_spec": revised_requirement_spec,
            **change_meta,
        }

    async def iterate_demo(
        self,
        brief: Any = None,
        requirement_spec: Any = None,
        current_demo_html: str = "",
        current_prd: Optional[str] = None,
        change_type: str = "",
        target_module: str = "demo",
        affected_pages: Optional[List[str]] = None,
        instruction: str = "",
        model_config: Any = None,
    ) -> Dict[str, Any]:
        if not str(instruction or "").strip():
            raise ValueError("请填写本次修改说明。")
        if not str(current_demo_html or "").strip():
            raise ValueError("当前 Demo 内容不能为空。")
        resolved_requirement_spec = await self.resolve_requirement_spec(
            brief=brief,
            requirement_spec=requirement_spec,
            model_config=model_config,
        )
        change_request = {
            "change_type": change_type,
            "target_module": target_module or "demo",
            "affected_pages": affected_pages or [],
            "instruction": instruction,
        }
        revised_requirement_spec = await self.llm_service.revise_requirement_spec(
            resolved_requirement_spec,
            change_request,
            model_config=self.serialize_model_config(model_config),
        )
        demo_bundle = await self.llm_service.iterate_demo_html(
            requirement_spec=revised_requirement_spec,
            current_demo_html=current_demo_html,
            change_request=change_request,
            model_config=self.serialize_model_config(model_config),
        )
        prototype_outline = await self.llm_service.generate_prototype_outline(
            requirement_spec=revised_requirement_spec,
            demo_html=demo_bundle["demo_html"],
            prd_content=current_prd,
            demo_plan=demo_bundle.get("demo_plan"),
            model_config=self.serialize_model_config(model_config),
        )
        change_meta = self.llm_service.build_change_metadata(change_request, revised_requirement_spec)
        generation_meta = dict(demo_bundle.get("generation_meta") or {})
        phases_completed = list(generation_meta.get("phases_completed") or [])
        if "prototype_outline" not in phases_completed:
            phases_completed.append("prototype_outline")
        generation_meta["phases_completed"] = phases_completed
        return {
            "demo_html": demo_bundle["demo_html"],
            "prototype_outline": prototype_outline,
            "demo_quality": demo_bundle.get("demo_quality"),
            "generation_meta": generation_meta,
            "requirement_spec": revised_requirement_spec,
            **change_meta,
        }
