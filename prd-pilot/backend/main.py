"""PRD Pilot backend service.

Core workflow:
input -> requirement spec -> PRD / demo / prototype outline -> consistency check -> targeted iteration.
"""

import os
from typing import List, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

from services.use_cases import PRDPilotUseCases


load_dotenv()

app = FastAPI(
    title="PRD Pilot API",
    description="AI PRD and demo workspace for product managers.",
    version="4.0.0",
)

use_cases = PRDPilotUseCases()


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    import traceback

    if isinstance(exc, HTTPException):
        raise exc

    error_msg = f"{type(exc).__name__}: {exc}\n{''.join(traceback.format_exc())}"
    print("=" * 60)
    print("Server error:")
    print(error_msg)
    print("=" * 60)
    return JSONResponse(status_code=500, content={"error": str(exc), "detail": error_msg})


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ProductBrief(BaseModel):
    product_name: str = ""
    product_type: str = ""
    elevator_pitch: str = ""
    problem_statement: str = ""
    target_users: str = ""
    user_pain_points: str = ""
    key_scenarios: str = ""
    core_features: str = ""
    primary_pages_hint: str = ""
    page_count_preference: str = ""
    demo_focus: str = ""
    feature_preferences: str = ""
    success_metrics: str = ""
    constraints: str = ""
    tech_stack: str = ""
    delivery_notes: str = ""


class RequirementSpec(BaseModel):
    product_name: str = ""
    product_type: str = ""
    target_users: List[str] = Field(default_factory=list)
    user_pain_points: List[str] = Field(default_factory=list)
    core_scenarios: List[str] = Field(default_factory=list)
    key_features: List[str] = Field(default_factory=list)
    primary_pages: List[str] = Field(default_factory=list)
    user_flow: List[str] = Field(default_factory=list)
    style_preference: str = ""
    constraints: List[str] = Field(default_factory=list)
    success_criteria: List[str] = Field(default_factory=list)


class ModelConfig(BaseModel):
    provider: str = ""
    model: str = ""
    api_key: str = ""
    base_url: str = ""
    max_tokens: int = 0


class ProductRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    brief: Optional[ProductBrief] = None
    requirement_spec: Optional[RequirementSpec] = None
    prd_content: Optional[str] = None
    runtime_model_config: Optional[ModelConfig] = Field(default=None, alias="model_config")


class ConsistencyRequest(BaseModel):
    requirement_spec: RequirementSpec
    prd: str = ""
    demo_html: str = ""
    prototype_outline: str = ""


class IterationRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    brief: Optional[ProductBrief] = None
    requirement_spec: Optional[RequirementSpec] = None
    runtime_model_config: Optional[ModelConfig] = Field(default=None, alias="model_config")
    change_type: str = ""
    target_module: str = ""
    affected_pages: List[str] = Field(default_factory=list)
    instruction: str = ""
    current_prd: Optional[str] = None
    current_demo_html: Optional[str] = None
    current_prototype_outline: Optional[str] = None


class RequirementOnlyRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    brief: ProductBrief
    runtime_model_config: Optional[ModelConfig] = Field(default=None, alias="model_config")


class ModelConfigRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    runtime_model_config: Optional[ModelConfig] = Field(default=None, alias="model_config")


def serialize_brief(brief: ProductBrief) -> dict:
    return brief.model_dump()


def serialize_requirement_spec(spec: RequirementSpec) -> dict:
    return spec.model_dump()


def serialize_model_config(model_config: Optional[ModelConfig]) -> Optional[dict]:
    return model_config.model_dump() if model_config else None


def validate_brief(brief: ProductBrief) -> None:
    required_fields = [
        brief.product_name,
        brief.problem_statement,
        brief.target_users,
        brief.user_pain_points,
        brief.key_scenarios,
        brief.core_features,
    ]
    if not any(value.strip() for value in required_fields):
        raise HTTPException(
            status_code=400,
            detail="请至少填写需求描述、产品名称、目标用户、用户痛点、核心场景或核心功能中的一项。",
        )


async def resolve_requirement_spec(
    llm_service,
    brief: Optional[ProductBrief],
    requirement_spec: Optional[RequirementSpec],
    model_config: Optional[ModelConfig] = None,
) -> dict:
    if requirement_spec:
        return serialize_requirement_spec(requirement_spec)
    if not brief:
        raise HTTPException(status_code=400, detail="缺少 brief 或 requirement_spec，无法继续处理。")
    validate_brief(brief)
    return await llm_service.structure_requirement(
        serialize_brief(brief),
        model_config=serialize_model_config(model_config),
    )


@app.get("/")
async def root():
    return {"status": "ok", "message": "PRD Pilot API is running"}


@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "PRD Pilot"}


@app.get("/api/model-options")
async def model_options():
    return {"success": True, "data": use_cases.get_model_options()}


@app.get("/api/test-llm")
async def test_llm():
    try:
        brief = {
            "product_name": "验证助手",
            "product_type": "Web 工具",
            "problem_statement": "帮助缺乏设计资源的产品同学快速整理需求并生成可演示方案。",
            "target_users": "学生产品经理、独立开发者",
            "user_pain_points": "不会系统写 PRD，也很难快速做出可评审 Demo。",
            "key_scenarios": "需求评审前快速准备 PRD 与演示页面。",
            "core_features": "需求结构化、PRD 生成、Demo 生成、一致性检查",
            "tech_stack": "后台管理台",
        }
        requirement_spec = await use_cases.llm_service.structure_requirement(brief)
        result = await use_cases.llm_service.generate_prd(requirement_spec)
        return {
            "status": "success",
            "message": "LLM connection is healthy",
            "requirement_spec": requirement_spec,
            "test_result": result[:160],
        }
    except ValueError as exc:
        return JSONResponse(status_code=400, content={"status": "error", "message": str(exc)})
    except Exception as exc:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(exc)})


@app.post("/api/test-model-config")
async def test_model_config(request: ModelConfigRequest):
    try:
        result = use_cases.test_model_config(request.runtime_model_config)
        return {"success": True, "data": result, "message": "模型连接测试成功"}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"模型连接测试失败: {exc}")


@app.post("/api/structure-requirement")
async def structure_requirement(request: RequirementOnlyRequest):
    try:
        result = await use_cases.structure_requirement(
            request.brief,
            model_config=request.runtime_model_config,
        )
        return {
            "success": True,
            "data": result,
            "message": "需求摘要解析成功",
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"需求解析失败: {exc}")


@app.post("/api/generate-prd")
async def generate_prd(request: ProductRequest):
    try:
        result = await use_cases.generate_prd(
            brief=request.brief,
            requirement_spec=request.requirement_spec,
            model_config=request.runtime_model_config,
        )
        return {
            "success": True,
            "data": result,
            "message": "PRD 生成成功",
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"PRD 生成失败: {exc}")


@app.post("/api/generate-demo")
async def generate_demo(request: ProductRequest):
    try:
        result = await use_cases.generate_demo(
            brief=request.brief,
            requirement_spec=request.requirement_spec,
            prd_content=request.prd_content,
            model_config=request.runtime_model_config,
        )
        return {
            "success": True,
            "data": result,
            "message": "Demo 生成成功",
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Demo 生成失败: {exc}")


@app.post("/api/check-consistency")
async def check_consistency(request: ConsistencyRequest):
    try:
        report = await use_cases.check_consistency(
            requirement_spec=request.requirement_spec,
            prd=request.prd,
            demo_html=request.demo_html,
            prototype_outline=request.prototype_outline,
        )
        return {
            "success": True,
            "data": report,
            "message": "一致性检查完成",
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"一致性检查失败: {exc}")


@app.post("/api/iterate-prd")
async def iterate_prd(request: IterationRequest):
    try:
        result = await use_cases.iterate_prd(
            brief=request.brief,
            requirement_spec=request.requirement_spec,
            current_prd=request.current_prd or "",
            change_type=request.change_type,
            target_module=request.target_module,
            affected_pages=request.affected_pages,
            instruction=request.instruction,
            model_config=request.runtime_model_config,
        )
        return {
            "success": True,
            "data": result,
            "message": "PRD 更新成功",
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"PRD 更新失败: {exc}")


@app.post("/api/iterate-demo")
async def iterate_demo(request: IterationRequest):
    try:
        result = await use_cases.iterate_demo(
            brief=request.brief,
            requirement_spec=request.requirement_spec,
            current_demo_html=request.current_demo_html or "",
            current_prd=request.current_prd,
            change_type=request.change_type,
            target_module=request.target_module,
            affected_pages=request.affected_pages,
            instruction=request.instruction,
            model_config=request.runtime_model_config,
        )
        return {
            "success": True,
            "data": result,
            "message": "Demo 更新成功",
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Demo 更新失败: {exc}")


if __name__ == "__main__":
    import uvicorn

    host = os.getenv("APP_HOST", "0.0.0.0")
    port = int(os.getenv("APP_PORT", 8000))
    uvicorn.run(app, host=host, port=port)


