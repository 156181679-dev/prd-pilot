from fastapi.testclient import TestClient

import main
from services.errors import WorkflowStageError


class FailingUseCases:
    def get_model_options(self):
        return {"providers": [], "default_config": {}}

    async def generate_demo(self, **kwargs):
        raise WorkflowStageError(
            error_code="demo_render_timeout",
            stage="html_render",
            detail="Demo HTML 渲染阶段失败：超时。",
            retryable=True,
            status_code=504,
        )


def test_generate_demo_returns_structured_error(monkeypatch):
    monkeypatch.setattr(main, "use_cases", FailingUseCases())
    client = TestClient(main.app)

    response = client.post(
        "/api/generate-demo",
        json={
            "brief": {
                "product_name": "Mock 产品",
                "problem_statement": "测试",
            }
        },
    )

    assert response.status_code == 504
    payload = response.json()
    assert payload["detail"]["error_code"] == "demo_render_timeout"
    assert payload["detail"]["stage"] == "html_render"
    assert payload["detail"]["retryable"] is True
