"""Deterministic mock LLM service used by tests and CI."""

from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional

from .errors import WorkflowStageError
from .llm_service import LLMService


class MockLLMService(LLMService):
    def __init__(self):
        super().__init__()

    def _mock_demo_mode(self, model_config: Optional[Dict[str, Any]] = None) -> str:
        requested_model = str((model_config or {}).get("model") or "").strip().lower()
        if requested_model in {"mock-timeout", "mock-quality-fail"}:
            return "timeout" if requested_model == "mock-timeout" else "quality_fail"
        return (os.getenv("PRD_PILOT_MOCK_DEMO_MODE") or "success").strip().lower()

    def test_model_config(self, model_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        config = self.resolve_model_config(
            model_config
            or {
                "provider": "mock",
                "api_key": "mock",
                "base_url": "http://mock.local",
                "model": "mock-prd-pilot",
            }
        )
        return {
            "provider": config["provider"],
            "model": config["model"],
            "base_url": config["base_url"],
            "message": "ok",
        }

    async def structure_requirement(
        self,
        brief: Dict[str, Any],
        model_config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        seed = self._build_requirement_seed(brief)
        seed["product_name"] = (brief.get("product_name") or "").strip() or "Mock 产品"
        seed["product_type"] = (brief.get("product_type") or "").strip() or "Web 工具"
        return self._normalize_spec(seed, seed)

    async def revise_requirement_spec(
        self,
        requirement_spec: Dict[str, Any],
        change_request: Dict[str, Any],
        model_config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        spec = self._normalize_spec(requirement_spec, requirement_spec)
        instruction = str(change_request.get("instruction") or "").strip()
        if instruction:
            spec["success_criteria"] = self._dedupe_preserve_order(spec["success_criteria"] + [instruction])
        if change_request.get("change_type") == "add_page":
            page_name = (change_request.get("affected_pages") or ["新增页面"])[0]
            spec["primary_pages"] = self._dedupe_preserve_order(spec["primary_pages"] + [page_name])
        return spec

    async def generate_prd(
        self,
        requirement_spec: Dict[str, Any],
        model_config: Optional[Dict[str, Any]] = None,
    ) -> str:
        spec = self._normalize_spec(requirement_spec, requirement_spec)
        return f"""# {spec['product_name']}

## 1. 背景与目标
- 围绕 {spec['product_type']} 场景构建可评审方案。

## 2. 目标用户
- {'；'.join(spec['target_users'])}

## 3. 核心场景
- {'；'.join(spec['core_scenarios'])}

## 4. 功能需求表
| 模块 | 需求描述 | 优先级 | 验证方式 |
| --- | --- | --- | --- |
| 核心模块 | {'；'.join(spec['key_features'])} | P0 | 页面演示 |

## 5. 业务流程
```mermaid
flowchart LR
  A[总览] --> B[核心任务]
  B --> C[结果反馈]
```

## 6. Demo 验证点
- 页面覆盖：{'、'.join(spec['primary_pages'])}

## 7. 风险与待确认项
- 需要继续验证：{'、'.join(spec['success_criteria'])}
"""

    async def generate_demo_plan(
        self,
        requirement_spec: Dict[str, Any],
        prd_content: Optional[str] = None,
        model_config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        spec = self._normalize_spec(requirement_spec, requirement_spec)
        pages = []
        for index, name in enumerate(spec["primary_pages"][:3] or ["总览页", "核心任务页", "结果反馈页"]):
            pages.append(
                {
                    "name": name,
                    "purpose": f"用于展示{name}的需求价值",
                    "key_modules": spec["key_features"][:3],
                    "entry_actions": ["点击进入", "查看详情"] if index == 0 else ["继续操作"],
                    "exit_actions": ["进入下一步"] if index < 2 else ["完成评审"],
                }
            )
        return {
            "pages": pages,
            "main_flow": ["进入总览页", "执行核心任务", "查看结果反馈"],
            "key_states": ["草稿", "评审中", "已完成", "空状态"],
            "interaction_requirements": ["关键按钮必须切换视图并显示反馈"],
            "visual_direction": "清晰的 PM 工作台风格，偏评审与演示场景",
        }

    def _mock_demo_html(self, requirement_spec: Dict[str, Any], demo_plan: Dict[str, Any], instruction: str = "") -> str:
        spec = self._normalize_spec(requirement_spec, requirement_spec)
        pages = demo_plan.get("pages") or []
        nav_buttons = "".join(
            f"<button class='nav-btn' onclick=\"showView('{page['name']}')\">{page['name']}</button>"
            for page in pages
        )
        sections = []
        for index, page in enumerate(pages):
            page_name = page["name"]
            hidden = "display:none;" if index else ""
            sections.append(
                f"""
                <section class="view" id="view-{page_name}" style="{hidden}">
                  <header class="view-head">
                    <h2>{page_name}</h2>
                    <span class="status">评审中</span>
                  </header>
                  <div class="grid">
                    <article class="panel">
                      <h3>关键模块</h3>
                      <ul>{''.join(f'<li>{item}</li>' for item in (page.get('key_modules') or spec['key_features'][:3]))}</ul>
                    </article>
                    <article class="panel">
                      <h3>验证说明</h3>
                      <p>{page.get('purpose')}</p>
                      <p>{instruction or '当前为 mock Demo，用于验证主链路与状态切换。'}</p>
                    </article>
                  </div>
                  <div class="actions">
                    <button onclick="advance('{page_name}')">继续操作</button>
                    <button class="ghost" onclick="setState('已完成')">标记完成</button>
                  </div>
                  <p class="feedback">当前状态：<strong id="state-{page_name}">草稿</strong></p>
                </section>
                """
            )
        return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{spec['product_name']} Demo</title>
  <style>
    body {{ margin: 0; font-family: Arial, sans-serif; background: #f4efe7; color: #18322d; }}
    .app {{ padding: 24px; }}
    .hero {{ display: flex; justify-content: space-between; align-items: center; gap: 16px; }}
    .hero-card, .panel {{ background: #fff; border-radius: 18px; padding: 20px; box-shadow: 0 12px 30px rgba(24,50,45,.08); }}
    .hero-card {{ flex: 1; }}
    .nav {{ display: flex; flex-wrap: wrap; gap: 10px; margin: 18px 0; }}
    .nav-btn, .actions button {{ border: none; border-radius: 999px; padding: 10px 16px; background: #2a9d8f; color: #fff; cursor: pointer; }}
    .actions .ghost {{ background: #e9dcc9; color: #18322d; }}
    .grid {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; }}
    .status {{ display: inline-flex; padding: 4px 10px; border-radius: 999px; background: #efe8db; }}
    .feedback {{ margin-top: 14px; }}
    .empty {{ border: 1px dashed #c7b49c; padding: 12px; border-radius: 14px; color: #7a6a58; }}
  </style>
</head>
<body>
  <div class="app">
    <div class="hero">
      <div class="hero-card">
        <p>Mock 工作台</p>
        <h1>{spec['product_name']}</h1>
        <p>{'，'.join(spec['core_scenarios'])}</p>
      </div>
      <div class="hero-card">
        <h3>状态概览</h3>
        <div class="empty">草稿 / 评审中 / 已完成 / 空状态</div>
      </div>
    </div>
    <div class="nav">{nav_buttons}</div>
    {''.join(sections)}
  </div>
  <script>
    const views = {json.dumps([page['name'] for page in pages], ensure_ascii=False)};
    function showView(name) {{
      views.forEach((item) => {{
        const el = document.getElementById(`view-${{item}}`);
        if (el) el.style.display = item === name ? 'block' : 'none';
      }});
    }}
    function advance(current) {{
      const index = views.indexOf(current);
      const next = views[Math.min(index + 1, views.length - 1)];
      showView(next);
      setState('评审中');
    }}
    function setState(value) {{
      views.forEach((item) => {{
        const el = document.getElementById(`state-${{item}}`);
        if (el && el.parentElement && el.parentElement.parentElement.style.display !== 'none') {{
          el.textContent = value;
        }}
      }});
    }}
  </script>
</body>
</html>"""

    async def generate_demo_html(
        self,
        requirement_spec: Dict[str, Any],
        prd_content: Optional[str] = None,
        model_config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        mode = self._mock_demo_mode(model_config)
        if mode == "timeout":
            raise WorkflowStageError(
                error_code="demo_render_timeout",
                stage="html_render",
                detail="Mock Demo HTML 渲染超时。",
                retryable=True,
                status_code=504,
            )
        if mode == "quality_fail":
            raise WorkflowStageError(
                error_code="demo_quality_failed",
                stage="quality_gate",
                detail="Mock Demo 质量门禁未通过。",
                retryable=True,
                status_code=422,
            )

        demo_plan = await self.generate_demo_plan(requirement_spec, prd_content=prd_content, model_config=model_config)
        html = self._mock_demo_html(requirement_spec, demo_plan)
        demo_quality = self._assess_demo_quality(requirement_spec, html, prd_content=prd_content)
        generation_meta = self._build_generation_meta(
            ["demo_plan", "html_render", "html_completion", "quality_gate"],
            demo_quality,
            repair_attempted=False,
            repair_succeeded=False,
        )
        return {
            "demo_plan": demo_plan,
            "demo_html": html,
            "demo_quality": demo_quality,
            "generation_meta": generation_meta,
        }

    async def generate_prototype_outline(
        self,
        requirement_spec: Dict[str, Any],
        prd_content: Optional[str] = None,
        demo_html: Optional[str] = None,
        demo_plan: Optional[Dict[str, Any]] = None,
        model_config: Optional[Dict[str, Any]] = None,
    ) -> str:
        spec = self._normalize_spec(requirement_spec, requirement_spec)
        return f"""## 页面结构
- {'、'.join(spec['primary_pages'])}

## 关键模块
- {'、'.join(spec['key_features'])}

## 用户操作路径
- 从总览进入核心任务，再查看结果反馈。

## 验证目标
- 验证需求表达、一致性检查和定点修改闭环。"""

    async def iterate_prd(
        self,
        requirement_spec: Dict[str, Any],
        current_prd: str,
        change_request: Dict[str, Any],
        model_config: Optional[Dict[str, Any]] = None,
    ) -> str:
        return current_prd + f"\n\n## 本轮修改\n- {change_request.get('instruction') or '已按结构化指令更新。'}\n"

    async def iterate_demo_html(
        self,
        requirement_spec: Dict[str, Any],
        current_demo_html: str,
        change_request: Dict[str, Any],
        prd_content: Optional[str] = None,
        model_config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        mode = self._mock_demo_mode(model_config)
        if mode == "timeout":
            raise WorkflowStageError(
                error_code="demo_iteration_timeout",
                stage="demo_iteration",
                detail="Mock Demo 更新超时。",
                retryable=True,
                status_code=504,
            )
        demo_plan = await self.generate_demo_plan(requirement_spec, prd_content=prd_content, model_config=model_config)
        html = self._mock_demo_html(requirement_spec, demo_plan, instruction=str(change_request.get("instruction") or ""))
        demo_quality = self._assess_demo_quality(requirement_spec, html, prd_content=prd_content)
        generation_meta = self._build_generation_meta(
            ["demo_iteration", "html_completion", "quality_gate"],
            demo_quality,
            repair_attempted=False,
            repair_succeeded=False,
        )
        return {
            "demo_plan": demo_plan,
            "demo_html": html,
            "demo_quality": demo_quality,
            "generation_meta": generation_meta,
        }
