from services.mock_llm_service import MockLLMService


def test_consistency_report_contains_evidence_and_repair_actions():
    service = MockLLMService()
    requirement_spec = {
        "product_name": "Mock 产品",
        "product_type": "Web 工具",
        "target_users": ["学生 PM"],
        "user_pain_points": ["需求整理慢"],
        "core_scenarios": ["评审前快速成稿"],
        "key_features": ["PRD 生成", "Demo 生成", "一致性检查"],
        "primary_pages": ["总览页", "核心任务页", "结果页"],
        "user_flow": ["总览页 -> 核心任务页 -> 结果页"],
        "style_preference": "后台管理台",
        "constraints": ["单文件 HTML"],
        "success_criteria": ["可完成评审演示"],
    }

    report = service.check_consistency(
        requirement_spec=requirement_spec,
        prd="# Mock 产品\n\n## 1. 背景与目标\n- 保留 PRD 生成",
        demo_html="<!DOCTYPE html><html><body><button>查看总览页</button></body></html>",
        prototype_outline="## 页面结构\n- 总览页",
    )

    assert "checks" in report
    assert "issues" in report
    assert "repair_actions" in report
    assert any("evidence" in item for item in report["checks"])
    assert any("severity" in issue for issue in report["issues"])
