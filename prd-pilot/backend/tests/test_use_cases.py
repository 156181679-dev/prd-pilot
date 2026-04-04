import pytest

from services.use_cases import PRDPilotUseCases


class FakeLLMService:
    async def structure_requirement(self, brief, model_config=None):
        return {
            "product_name": brief.get("product_name") or "Mock 产品",
            "product_type": "Web 工具",
            "target_users": ["学生 PM"],
            "user_pain_points": ["需求整理慢"],
            "core_scenarios": ["评审前快速成稿"],
            "key_features": ["PRD 生成", "Demo 生成"],
            "primary_pages": ["总览页", "核心任务页", "结果页"],
            "user_flow": ["总览页 -> 核心任务页 -> 结果页"],
            "style_preference": "后台管理台",
            "constraints": ["单文件 HTML"],
            "success_criteria": ["可完成评审演示"],
        }

    async def generate_prd(self, requirement_spec, model_config=None):
        return "# Mock 产品\n\n## 1. 背景与目标\n- 测试用 PRD\n"

    async def generate_demo_html(self, requirement_spec, prd_content=None, model_config=None):
        return {
            "demo_plan": {"pages": [{"name": "总览页"}]},
            "demo_html": "<!DOCTYPE html><html><body><button onclick=\"go()\">进入</button></body></html>",
            "demo_quality": {"status": "pass", "score": 88},
            "generation_meta": {
                "phases_completed": ["demo_plan", "html_render", "html_completion", "quality_gate"],
                "repair_attempted": False,
                "repair_succeeded": False,
            },
        }

    async def generate_prototype_outline(self, requirement_spec, prd_content=None, demo_html=None, demo_plan=None, model_config=None):
        return "## 页面结构\n- 总览页\n"

    async def revise_requirement_spec(self, requirement_spec, change_request, model_config=None):
        updated = dict(requirement_spec)
        updated["success_criteria"] = requirement_spec["success_criteria"] + [change_request["instruction"]]
        return updated

    async def iterate_prd(self, requirement_spec, current_prd, change_request, model_config=None):
        return current_prd + "\n## 本轮修改\n- 已更新\n"

    async def iterate_demo_html(self, requirement_spec, current_demo_html, change_request, prd_content=None, model_config=None):
        return {
            "demo_plan": {"pages": [{"name": "结果页"}]},
            "demo_html": "<!DOCTYPE html><html><body><button onclick=\"go()\">继续</button></body></html>",
            "demo_quality": {"status": "pass", "score": 90},
            "generation_meta": {
                "phases_completed": ["demo_iteration", "html_completion", "quality_gate"],
                "repair_attempted": False,
                "repair_succeeded": False,
            },
        }

    def check_consistency(self, requirement_spec, prd, demo_html, prototype_outline):
        return {
            "overall_level": "high",
            "score": 92,
            "checks": [{"id": "page_coverage", "label": "页面覆盖", "status": "pass", "summary": "ok", "evidence": "all good", "missing": []}],
            "issues": [],
            "repair_actions": [],
            "repair_suggestions": [],
        }

    def build_change_metadata(self, change_request, requirement_spec):
        return {
            "change_summary": "已更新 Demo",
            "changed_sections": ["关键模块"],
            "affected_pages": ["结果页"],
        }


@pytest.mark.asyncio
async def test_generate_demo_returns_quality_and_generation_meta():
    use_cases = PRDPilotUseCases(llm_service=FakeLLMService())

    result = await use_cases.generate_demo(
        brief={"product_name": "Mock 产品", "problem_statement": "测试"},
        model_config={"provider": "mock"},
    )

    assert result["demo_html"].startswith("<!DOCTYPE html>")
    assert result["demo_quality"]["score"] == 88
    assert "prototype_outline" in result
    assert result["generation_meta"]["phases_completed"][-1] == "prototype_outline"


@pytest.mark.asyncio
async def test_iterate_demo_returns_change_meta_and_generation_meta():
    use_cases = PRDPilotUseCases(llm_service=FakeLLMService())

    result = await use_cases.iterate_demo(
        brief={"product_name": "Mock 产品", "problem_statement": "测试"},
        current_demo_html="<!DOCTYPE html><html><body></body></html>",
        current_prd="# Mock",
        change_type="clarify_flow",
        target_module="demo",
        affected_pages=["结果页"],
        instruction="补一个结果页",
        model_config={"provider": "mock"},
    )

    assert result["demo_quality"]["status"] == "pass"
    assert result["change_summary"] == "已更新 Demo"
    assert result["affected_pages"] == ["结果页"]
    assert "prototype_outline" in result["generation_meta"]["phases_completed"]
