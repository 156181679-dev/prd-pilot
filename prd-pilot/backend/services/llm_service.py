"""LLM service for PRD Pilot's requirement validation workflow."""

import json
import os
import re
import sys
from typing import Any, Dict, List, Optional, Tuple

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


DEFAULT_PROVIDER = "deepseek"
DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"
DEFAULT_MODEL = "deepseek-chat"
DEFAULT_MAX_TOKENS = 0
HTML_CONTINUATION_ATTEMPTS = 2
HTML_TAIL_WINDOW = 12000

PROVIDER_OPTIONS = [
    {
        "id": "deepseek",
        "label": "DeepSeek",
        "base_url": "https://api.deepseek.com/v1",
        "models": [
            {"id": "deepseek-chat", "label": "deepseek-chat"},
            {"id": "deepseek-reasoner", "label": "deepseek-reasoner"},
        ],
    },
    {
        "id": "openai",
        "label": "OpenAI",
        "base_url": "https://api.openai.com/v1",
        "models": [
            {"id": "gpt-4.1-mini", "label": "gpt-4.1-mini"},
            {"id": "gpt-4.1", "label": "gpt-4.1"},
            {"id": "gpt-4o-mini", "label": "gpt-4o-mini"},
            {"id": "gpt-4o", "label": "gpt-4o"},
            {"id": "gpt-5-mini", "label": "gpt-5-mini"},
            {"id": "gpt-5", "label": "gpt-5"},
        ],
    },
    {
        "id": "openrouter",
        "label": "OpenRouter",
        "base_url": "https://openrouter.ai/api/v1",
        "models": [
            {"id": "openai/gpt-4.1-mini", "label": "openai/gpt-4.1-mini"},
            {"id": "deepseek/deepseek-chat-v3-0324", "label": "deepseek/deepseek-chat-v3-0324"},
            {"id": "anthropic/claude-3.7-sonnet", "label": "anthropic/claude-3.7-sonnet"},
            {"id": "google/gemini-2.5-flash", "label": "google/gemini-2.5-flash"},
        ],
    },
    {
        "id": "zhipu",
        "label": "Zhipu / GLM",
        "base_url": "https://open.bigmodel.cn/api/paas/v4/",
        "models": [
            {"id": "glm-4.5-air", "label": "glm-4.5-air"},
            {"id": "glm-4.5", "label": "glm-4.5"},
            {"id": "glm-4-plus", "label": "glm-4-plus"},
        ],
    },
    {
        "id": "siliconflow",
        "label": "SiliconFlow",
        "base_url": "https://api.siliconflow.cn/v1",
        "models": [
            {"id": "Qwen/Qwen3-32B", "label": "Qwen/Qwen3-32B"},
            {"id": "deepseek-ai/DeepSeek-V3", "label": "deepseek-ai/DeepSeek-V3"},
            {"id": "THUDM/GLM-4-9B-Chat", "label": "THUDM/GLM-4-9B-Chat"},
        ],
    },
    {
        "id": "moonshot",
        "label": "Moonshot",
        "base_url": "https://api.moonshot.cn/v1",
        "models": [
            {"id": "moonshot-v1-8k", "label": "moonshot-v1-8k"},
            {"id": "moonshot-v1-32k", "label": "moonshot-v1-32k"},
            {"id": "moonshot-v1-128k", "label": "moonshot-v1-128k"},
        ],
    },
    {
        "id": "groq",
        "label": "Groq",
        "base_url": "https://api.groq.com/openai/v1",
        "models": [
            {"id": "llama-3.3-70b-versatile", "label": "llama-3.3-70b-versatile"},
            {"id": "llama-3.1-8b-instant", "label": "llama-3.1-8b-instant"},
            {"id": "openai/gpt-oss-20b", "label": "openai/gpt-oss-20b"},
        ],
    },
    {
        "id": "dashscope",
        "label": "DashScope / Qwen",
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "models": [
            {"id": "qwen-turbo", "label": "qwen-turbo"},
            {"id": "qwen-plus", "label": "qwen-plus"},
            {"id": "qwen-max", "label": "qwen-max"},
        ],
    },
    {
        "id": "ollama",
        "label": "Ollama (Local)",
        "base_url": "http://localhost:11434/v1",
        "models": [
            {"id": "qwen2.5:7b", "label": "qwen2.5:7b"},
            {"id": "llama3.1:8b", "label": "llama3.1:8b"},
            {"id": "deepseek-r1:8b", "label": "deepseek-r1:8b"},
        ],
    },
    {
        "id": "custom",
        "label": "Custom OpenAI Compatible",
        "base_url": "",
        "models": [],
    },
]

PROVIDER_PRESETS = {item["id"]: item for item in PROVIDER_OPTIONS}

STRUCTURED_KEYS = [
    "product_name",
    "product_type",
    "target_users",
    "user_pain_points",
    "core_scenarios",
    "key_features",
    "primary_pages",
    "user_flow",
    "style_preference",
    "constraints",
    "success_criteria",
]

CHANGE_TYPE_LABELS = {
    "modify_user": "调整目标用户",
    "add_page": "新增页面",
    "remove_feature": "删除功能",
    "adjust_layout": "调整布局层级",
    "change_style": "切换原型风格",
    "improve_data_density": "强化数据展示",
    "simplify_prd": "精简 PRD",
    "clarify_flow": "梳理关键流程",
}

CHANGE_SECTION_HINTS = {
    "modify_user": ["目标用户", "核心场景", "验证目标"],
    "add_page": ["页面结构", "关键模块", "用户操作路径"],
    "remove_feature": ["功能需求表", "关键模块", "用户操作路径"],
    "adjust_layout": ["页面结构", "交互布局", "关键模块"],
    "change_style": ["视觉风格", "页面结构", "关键模块"],
    "improve_data_density": ["数据展示", "关键模块", "Demo 交互"],
    "simplify_prd": ["背景与目标", "功能需求表", "风险与待确认项"],
    "clarify_flow": ["业务流程", "用户操作路径", "验证目标"],
}


def get_model_options() -> Dict[str, Any]:
    env_provider = (os.getenv("OPENAI_PROVIDER") or DEFAULT_PROVIDER).strip() or DEFAULT_PROVIDER
    raw_max_tokens = (os.getenv("OPENAI_MAX_TOKENS") or str(DEFAULT_MAX_TOKENS)).strip() or str(DEFAULT_MAX_TOKENS)
    try:
        default_max_tokens = int(raw_max_tokens)
    except ValueError:
        default_max_tokens = DEFAULT_MAX_TOKENS
    return {
        "providers": PROVIDER_OPTIONS,
        "default_config": {
            "provider": env_provider if env_provider in PROVIDER_PRESETS else DEFAULT_PROVIDER,
            "base_url": (os.getenv("OPENAI_BASE_URL") or DEEPSEEK_BASE_URL).strip(),
            "model": (os.getenv("OPENAI_MODEL") or DEFAULT_MODEL).strip(),
            "max_tokens": max(0, default_max_tokens),
            "has_env_api_key": bool((os.getenv("OPENAI_API_KEY") or "").strip() and not (os.getenv("OPENAI_API_KEY") or "").strip().startswith("your_")),
        },
    }


REQUIREMENT_SPEC_SYSTEM_PROMPT = """你是需求结构化分析助手。
请根据用户输入，抽取并补齐一份 Requirement Spec。
要求：
1. 只返回 JSON 对象，不要 Markdown，不要解释。
2. JSON 必须严格包含以下键：
   product_name, product_type, target_users, user_pain_points, core_scenarios,
   key_features, primary_pages, user_flow, style_preference, constraints, success_criteria
3. 其中 product_name、product_type、style_preference 为字符串，其余字段必须是字符串数组。
4. 输出要具体、可评审、可用于驱动后续 PRD 和 Demo 生成。
5. 若用户输入不完整，可做合理推断，但不要输出空数组；至少给出 1 条具体内容。
"""


PRD_SYSTEM_PROMPT = """你是一位擅长辅助撰写 PRD 的产品分析助手。
请基于 Requirement Spec 输出一份可继续编辑的中文 PRD 初稿。
要求：
1. 输出简体中文 Markdown，不要额外解释。
2. 语气务实，像协助完成评审材料，而不是宣传文案。
3. 固定结构：
   - # 产品名称
   - ## 1. 背景与目标
   - ## 2. 目标用户
   - ## 3. 核心场景
   - ## 4. 功能需求表
   - ## 5. 业务流程
   - ## 6. Demo 验证点
   - ## 7. 风险与待确认项
4. “功能需求表”必须是 Markdown 表格，列包含：模块、需求描述、优先级、验证方式。
5. “业务流程”必须包含 Mermaid 流程图代码。
6. 内容要与 Requirement Spec 保持命名一致。
"""


DEMO_SYSTEM_PROMPT = """你是一位前端原型工程师。
请基于 Requirement Spec 生成一个可演示需求的单文件 HTML Demo。
要求：
1. 只返回完整 HTML，不要 Markdown 代码块，不要解释。
2. 必须包含内联 CSS 和内联 JavaScript，可直接通过 iframe srcdoc 预览。
3. 只能使用本地代码，不依赖外部 CDN、字体或图片。
4. Demo 必须体现清晰主线：总览页、核心任务页、关键操作流程、结果或反馈状态。
5. 页面之间必须能串起来，不能只是拼接静态模板。
6. 所有主要按钮都必须绑定真实交互，禁止死按钮。
7. 如果包含登录、注册、开始使用等入口按钮，点击后必须进入主页面或下一步视图。
8. 必须带有真实感假数据、状态标签、空状态或风险提示，不要输出空白模板块。
9. 视觉上要统一且有层次，但重点是“可演示”和“可评审”，不是堆砌复杂样式。
10. 控制代码体量，优先保证结构完整、交互完整和 HTML 闭合完整。
"""


PROTOTYPE_OUTLINE_PROMPT = """你是一位原型说明助手。
请输出一份中文 Markdown 原型说明，用于帮助用户快速评审页面结构和验证目标。
要求：
1. 固定结构：
   - ## 页面结构
   - ## 关键模块
   - ## 用户操作路径
   - ## 验证目标
2. 说明要基于 Requirement Spec 和 Demo，总结页面分区、交互主线与验证重点。
3. 不要复述整份 PRD，也不要输出图片描述。
"""


SPEC_ITERATION_PROMPT = """你是一位 Requirement Spec 修订助手。
你会收到当前 Requirement Spec 和一条结构化编辑指令，请输出更新后的 Requirement Spec JSON。
要求：
1. 只返回 JSON 对象，不要 Markdown，不要解释。
2. JSON 键必须保持与原始 Requirement Spec 完全一致。
3. 只修改与指令相关的字段，保留其余合理内容。
4. affected_pages 中提到的页面要优先体现在 primary_pages 或 user_flow 中。
5. 若指令要求修改风格、目标用户、功能、页面，必须同步更新相关字段，保持内部一致。
"""


PRD_ITERATION_PROMPT = """你是一位 PRD 修订助手。
你会收到当前 Requirement Spec、当前 PRD 和一条结构化编辑指令。
请输出吸收修改后的完整 Markdown PRD。
要求：
1. 只返回完整 Markdown，不要解释。
2. 保持原有合理内容，只对相关部分做定点修改。
3. 更新后内容必须与最新 Requirement Spec 保持一致。
4. 如果指令只影响局部，不要整份重写成完全不同的内容。
"""


DEMO_ITERATION_PROMPT = """你是一位前端原型工程师。
你会收到当前 Requirement Spec、当前 Demo HTML 和一条结构化编辑指令。
请输出更新后的完整 HTML。
要求：
1. 只返回完整 HTML，不要 Markdown，不要解释。
2. 只修改相关页面、模块、交互或视觉层次，不要无差别推翻重做。
3. 更新后仍需保留可演示主线、真实感假数据、状态变化与关键按钮交互。
4. 如果指令涉及 affected_pages，优先调整这些页面。
5. 保证最终 HTML 结构完整，包含 </body> 和 </html>。
"""


CONTINUE_HTML_SYSTEM_PROMPT = """你是一位严格的前端代码补全助手。
你会收到一段被截断的 HTML，请只输出缺失的后续部分。
要求：
1. 只输出需要追加的代码片段，不要重复已有开头。
2. 不要解释，不要 Markdown 代码块。
3. 优先补全被截断的 CSS、JS 和 HTML 结构。
4. 如果尚未闭合，最终必须补到 </body> 和 </html>。
"""


STYLE_GUIDES = {
    "原生 HTML 原型": """原型风格：原生 HTML 原型
- 优先生成适合直接演示和下载的单文件 HTML 页面
- 布局清晰、直接、轻量，但不能单薄
- 允许使用 hero 区、重点卡片和 1 到 2 个关键交互流程
- 重点是让需求一眼可懂，可快速演示""",
    "Vue 风格": """原型风格：Vue 风格
- 页面要体现组件化思路，模块边界清晰
- 多使用卡片分组、标签切换、信息面板、分区容器
- 视觉上轻盈、规整、适合中后台或 SaaS 产品""",
    "React 风格": """原型风格：React 风格
- 页面要体现状态驱动、工作台式布局和区块化信息分层
- 更强调数据区块、操作区、反馈区之间的关系
- 适合仪表盘、协作工具、内容管理或运营工作台""",
    "移动端 H5": """原型风格：移动端 H5
- 以手机视口为主进行设计，使用单列布局
- 使用卡片流、吸底主按钮、顶部标题栏和分段内容区
- 重点突出触控友好和首屏主操作""",
    "后台管理台": """原型风格：后台管理台
- 使用后台管理布局，如侧边栏、顶部信息区、主工作区
- 首页优先包含统计卡片、筛选区、列表或任务面板
- 主次操作要清晰，支持状态切换和表单或表格交互""",
}


class LLMService:
    def __init__(self):
        self.default_provider = (os.getenv("OPENAI_PROVIDER") or DEFAULT_PROVIDER).strip() or DEFAULT_PROVIDER
        self.default_model = (os.getenv("OPENAI_MODEL") or DEFAULT_MODEL).strip()
        self.default_base_url = (os.getenv("OPENAI_BASE_URL") or DEEPSEEK_BASE_URL).strip()
        self.default_max_tokens = self._read_max_tokens()

    def _read_max_tokens(self) -> int:
        raw_value = (os.getenv("OPENAI_MAX_TOKENS") or str(DEFAULT_MAX_TOKENS)).strip()
        try:
            value = int(raw_value)
        except ValueError:
            return DEFAULT_MAX_TOKENS
        return max(0, value)

    def resolve_model_config(self, model_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        model_config = model_config or {}
        provider = (model_config.get("provider") or self.default_provider or DEFAULT_PROVIDER).strip()
        preset = PROVIDER_PRESETS.get(provider, PROVIDER_PRESETS[DEFAULT_PROVIDER])

        api_key = (model_config.get("api_key") or os.getenv("OPENAI_API_KEY") or "").strip()
        if provider == "ollama" and not api_key:
            api_key = "ollama"
        if not api_key or api_key.startswith("your_"):
            raise ValueError("请先在界面中填写有效的 API Key，或在 backend/.env 中配置默认 Key。")

        base_url = (model_config.get("base_url") or preset.get("base_url") or self.default_base_url).strip()
        model = (model_config.get("model") or "").strip()
        if not model:
            if preset.get("models"):
                model = preset["models"][0]["id"]
            else:
                model = self.default_model

        raw_max_tokens = model_config.get("max_tokens", self.default_max_tokens)
        try:
            max_tokens = max(0, int(raw_max_tokens))
        except (TypeError, ValueError):
            max_tokens = self.default_max_tokens

        if not base_url:
            raise ValueError("当前模型配置缺少 Base URL，请补充兼容 OpenAI 的接口地址。")

        if provider == "deepseek" and "deepseek.com" not in base_url:
            raise ValueError(f"DeepSeek 的 Base URL 应为 {DEEPSEEK_BASE_URL}。")

        return {
            "provider": provider,
            "api_key": api_key,
            "base_url": base_url,
            "model": model,
            "max_tokens": max_tokens,
        }

    def _build_client(self, model_config: Dict[str, Any]) -> OpenAI:
        return OpenAI(api_key=model_config["api_key"], base_url=model_config["base_url"])

    def _chat(
        self,
        system_prompt: str,
        user_prompt: str,
        model_config: Optional[Dict[str, Any]] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        resolved_config = self.resolve_model_config(model_config)
        payload = {
            "model": resolved_config["model"],
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.6,
        }

        effective_max_tokens = resolved_config["max_tokens"] if max_tokens is None else max_tokens
        if effective_max_tokens > 0:
            payload["max_tokens"] = effective_max_tokens

        response = self._build_client(resolved_config).chat.completions.create(**payload)
        return response.choices[0].message.content or ""

    def _clean_code_fence(self, content: str) -> str:
        cleaned = content.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```[a-zA-Z0-9_-]*\s*", "", cleaned)
            cleaned = re.sub(r"\s*```$", "", cleaned)
        return cleaned.strip()

    def _extract_json_object(self, content: str) -> Dict[str, Any]:
        cleaned = self._clean_code_fence(content)
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise ValueError("模型未返回有效的 JSON 结构。")
        json_text = cleaned[start : end + 1]
        return json.loads(json_text)

    def _normalize_text(self, value: str) -> str:
        return re.sub(r"[\s\-_./|,:;，。！？、()（）【】\[\]<>《》'\"]+", "", (value or "").lower())

    def _split_to_list(self, value: Any) -> List[str]:
        if value is None:
            return []
        if isinstance(value, list):
            items = value
        else:
            text = str(value)
            items = re.split(r"[\n\r,，;；、]+", text)
        cleaned = []
        seen = set()
        for item in items:
            item_text = str(item).strip().lstrip("-•0123456789. ")
            if not item_text:
                continue
            if item_text not in seen:
                cleaned.append(item_text)
                seen.add(item_text)
        return cleaned

    def _fallback_list(self, values: List[str], fallback: str) -> List[str]:
        return values if values else [fallback]

    def _build_requirement_seed(self, brief: Dict[str, str]) -> Dict[str, Any]:
        product_name = (brief.get("product_name") or "").strip() or "未命名需求"
        product_type = (brief.get("product_type") or "").strip() or "Web 工具"
        style_preference = (brief.get("tech_stack") or "").strip() or "不限定"

        target_users = self._fallback_list(
            self._split_to_list(brief.get("target_users")),
            "缺乏设计或前端资源、需要快速完成需求评审与演示的学生 PM 或独立开发者",
        )
        user_pain_points = self._fallback_list(
            self._split_to_list(brief.get("user_pain_points") or brief.get("problem_statement")),
            "需求表达不完整，难以快速整理成可评审材料",
        )
        core_scenarios = self._fallback_list(
            self._split_to_list(brief.get("key_scenarios") or brief.get("demo_focus")),
            "在需求评审前快速整理方案并生成可演示原型",
        )
        key_features = self._fallback_list(
            self._split_to_list(brief.get("core_features") or brief.get("feature_preferences")),
            "结构化需求整理、PRD 生成、Demo 生成、一致性检查",
        )
        primary_pages = self._fallback_list(
            self._split_to_list(brief.get("primary_pages_hint") or brief.get("page_count_preference")),
            "首页/总览页,核心任务页,结果反馈页",
        )
        user_flow = self._fallback_list(
            self._split_to_list(
                brief.get("demo_focus")
                or brief.get("delivery_notes")
                or "输入需求,确认摘要,生成 PRD,生成 Demo,查看验证结果"
            ),
            "输入需求 -> 结构化解析 -> 生成 PRD / Demo -> 检查一致性 -> 定点修改",
        )
        constraints = self._fallback_list(
            self._split_to_list(brief.get("constraints") or brief.get("delivery_notes")),
            "首版以可评审、可演示为目标，不追求复杂工程实现",
        )
        success_criteria = self._fallback_list(
            self._split_to_list(brief.get("success_metrics")),
            "能够在一次会话内完成需求整理、PRD 生成、Demo 生成与问题修复",
        )

        return {
            "product_name": product_name,
            "product_type": product_type,
            "target_users": target_users,
            "user_pain_points": user_pain_points,
            "core_scenarios": core_scenarios,
            "key_features": key_features,
            "primary_pages": primary_pages,
            "user_flow": user_flow,
            "style_preference": style_preference,
            "constraints": constraints,
            "success_criteria": success_criteria,
        }

    def format_product_brief(self, brief: Dict[str, str]) -> str:
        labels = {
            "product_name": "产品名称",
            "product_type": "产品类型",
            "elevator_pitch": "一句话定位",
            "problem_statement": "需求描述",
            "target_users": "目标用户",
            "user_pain_points": "用户痛点",
            "key_scenarios": "核心场景",
            "core_features": "核心功能点",
            "primary_pages_hint": "页面偏好",
            "page_count_preference": "页面数量偏好",
            "demo_focus": "重点演示场景",
            "feature_preferences": "界面偏好",
            "success_metrics": "成功标准",
            "constraints": "约束条件",
            "tech_stack": "原型风格",
            "delivery_notes": "补充说明",
        }
        lines = []
        for key, label in labels.items():
            value = (brief.get(key) or "").strip()
            if value:
                lines.append(f"{label}：{value}")
        return "\n".join(lines)

    def format_requirement_spec(self, requirement_spec: Dict[str, Any]) -> str:
        labels = {
            "product_name": "产品名称",
            "product_type": "产品类型",
            "target_users": "目标用户",
            "user_pain_points": "用户痛点",
            "core_scenarios": "核心场景",
            "key_features": "关键功能",
            "primary_pages": "主要页面",
            "user_flow": "用户流程",
            "style_preference": "原型风格",
            "constraints": "约束条件",
            "success_criteria": "成功标准",
        }
        lines = []
        for key in STRUCTURED_KEYS:
            value = requirement_spec.get(key)
            if isinstance(value, list):
                lines.append(f"{labels[key]}：")
                lines.extend([f"- {item}" for item in value])
            else:
                lines.append(f"{labels[key]}：{value}")
        return "\n".join(lines)

    def format_change_request(self, change_request: Dict[str, Any]) -> str:
        lines = [
            f"修改类型：{change_request.get('change_type') or '未指定'}",
            f"目标模块：{change_request.get('target_module') or '未指定'}",
            "影响页面：" + (", ".join(change_request.get("affected_pages") or []) or "未指定"),
            f"修改说明：{change_request.get('instruction') or ''}",
        ]
        return "\n".join(lines)

    def get_style_guidance(self, style_name: Optional[str]) -> str:
        style_name = (style_name or "").strip()
        if not style_name:
            return """原型风格：不限定
- 根据需求自行选择最适合评审和演示的页面结构
- 保持统一风格，不要混合后台、营销页和移动端样式
- 优先服务于主流程演示和信息表达"""
        return STYLE_GUIDES.get(
            style_name,
            f"""原型风格：{style_name}
- 按该风格统一页面结构、布局和视觉语言
- 不要只把风格写在文案里，必须落实到页面层次和交互上""",
        )

    def _normalize_spec(self, raw_spec: Dict[str, Any], seed: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        base = seed.copy() if seed else self._build_requirement_seed({})
        normalized = {}
        for key in STRUCTURED_KEYS:
            if key in {"product_name", "product_type", "style_preference"}:
                normalized[key] = str(raw_spec.get(key) or base.get(key) or "").strip()
            else:
                fallback_items = base.get(key) or []
                normalized[key] = self._fallback_list(
                    self._split_to_list(raw_spec.get(key)),
                    fallback_items[0] if fallback_items else "待补充",
                )
                if len(normalized[key]) == 1 and fallback_items:
                    normalized[key] = fallback_items if normalized[key][0] == fallback_items[0] else normalized[key]
        normalized["product_name"] = normalized["product_name"] or base.get("product_name") or "未命名需求"
        normalized["product_type"] = normalized["product_type"] or base.get("product_type") or "Web 工具"
        normalized["style_preference"] = normalized["style_preference"] or base.get("style_preference") or "不限定"
        return normalized

    def _is_complete_html(self, html: str) -> bool:
        lowered = html.lower()
        return "</body>" in lowered and "</html>" in lowered

    def _append_non_overlapping(self, base: str, addition: str) -> str:
        if not addition:
            return base

        max_overlap = min(len(base), len(addition), 2000)
        for overlap in range(max_overlap, 0, -1):
            if base[-overlap:] == addition[:overlap]:
                return base + addition[overlap:]
        return base + addition

    def _complete_html_if_needed(
        self,
        html: str,
        model_config: Optional[Dict[str, Any]] = None,
    ) -> str:
        completed = html
        if self._is_complete_html(completed):
            return completed

        for _ in range(HTML_CONTINUATION_ATTEMPTS):
            tail = completed[-HTML_TAIL_WINDOW:]
            continuation_prompt = f"""
下面这段 HTML 被截断了，请只续写缺失部分。
已生成内容（末尾）：
{tail}
"""
            addition = self._clean_code_fence(
                self._chat(
                    CONTINUE_HTML_SYSTEM_PROMPT,
                    continuation_prompt,
                    model_config=model_config,
                )
            )
            completed = self._append_non_overlapping(completed, addition)
            if self._is_complete_html(completed):
                break

        return completed

    def test_model_config(self, model_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        resolved_config = self.resolve_model_config(model_config)
        result = self._chat(
            "你是一个连接测试助手，请只回复 ok。",
            "请返回 ok，用于验证接口是否可用。",
            model_config=resolved_config,
            max_tokens=20,
        )
        return {
            "provider": resolved_config["provider"],
            "model": resolved_config["model"],
            "base_url": resolved_config["base_url"],
            "message": result.strip() or "ok",
        }

    async def structure_requirement(
        self,
        brief: Dict[str, str],
        model_config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        seed = self._build_requirement_seed(brief)
        prompt = f"""
请根据以下输入抽取 Requirement Spec。

用户输入：
{self.format_product_brief(brief)}

请按以下 JSON 结构返回：
{json.dumps(seed, ensure_ascii=False, indent=2)}
"""
        try:
            response = self._chat(
                REQUIREMENT_SPEC_SYSTEM_PROMPT,
                prompt,
                model_config=model_config,
                max_tokens=1800,
            )
            structured = self._extract_json_object(response)
            return self._normalize_spec(structured, seed)
        except Exception as exc:
            print(f"Requirement structuring fallback: {exc}", file=sys.stderr)
            return self._normalize_spec(seed, seed)

    async def revise_requirement_spec(
        self,
        requirement_spec: Dict[str, Any],
        change_request: Dict[str, Any],
        model_config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        seed = self._normalize_spec(requirement_spec, requirement_spec)
        prompt = f"""
当前 Requirement Spec：
{json.dumps(seed, ensure_ascii=False, indent=2)}

结构化编辑指令：
{self.format_change_request(change_request)}
"""
        try:
            response = self._chat(
                SPEC_ITERATION_PROMPT,
                prompt,
                model_config=model_config,
                max_tokens=1800,
            )
            revised = self._extract_json_object(response)
            return self._normalize_spec(revised, seed)
        except Exception as exc:
            print(f"Requirement spec iteration fallback: {exc}", file=sys.stderr)
            return seed

    async def generate_prd(
        self,
        requirement_spec: Dict[str, Any],
        model_config: Optional[Dict[str, Any]] = None,
    ) -> str:
        style_guidance = self.get_style_guidance(requirement_spec.get("style_preference"))
        user_prompt = f"""
请基于以下 Requirement Spec 生成 PRD：

{self.format_requirement_spec(requirement_spec)}

{style_guidance}
"""
        try:
            return self._chat(PRD_SYSTEM_PROMPT, user_prompt, model_config=model_config)
        except Exception as exc:
            print(f"PRD generation error: {exc}", file=sys.stderr)
            raise Exception(f"PRD 生成失败: {exc}")

    async def generate_demo_html(
        self,
        requirement_spec: Dict[str, Any],
        prd_content: Optional[str] = None,
        model_config: Optional[Dict[str, Any]] = None,
    ) -> str:
        style_guidance = self.get_style_guidance(requirement_spec.get("style_preference"))
        user_prompt = f"""
请基于以下 Requirement Spec 生成 Demo：

Requirement Spec：
{self.format_requirement_spec(requirement_spec)}

PRD：
{prd_content or '暂无 PRD，请主要基于 Requirement Spec 生成。'}

{style_guidance}
"""
        try:
            html = self._chat(DEMO_SYSTEM_PROMPT, user_prompt, model_config=model_config)
            cleaned = self._clean_code_fence(html)
            return self._complete_html_if_needed(cleaned, model_config=model_config)
        except Exception as exc:
            print(f"Demo generation error: {exc}", file=sys.stderr)
            raise Exception(f"Demo 生成失败: {exc}")

    async def generate_prototype_outline(
        self,
        requirement_spec: Dict[str, Any],
        prd_content: Optional[str] = None,
        demo_html: Optional[str] = None,
        model_config: Optional[Dict[str, Any]] = None,
    ) -> str:
        style_guidance = self.get_style_guidance(requirement_spec.get("style_preference"))
        user_prompt = f"""
请基于以下内容输出原型说明：

Requirement Spec：
{self.format_requirement_spec(requirement_spec)}

PRD：
{prd_content or '暂无'}

Demo HTML：
{demo_html or '暂无 Demo'}

{style_guidance}
"""
        try:
            return self._chat(PROTOTYPE_OUTLINE_PROMPT, user_prompt, model_config=model_config)
        except Exception as exc:
            print(f"Prototype outline generation error: {exc}", file=sys.stderr)
            raise Exception(f"原型说明生成失败: {exc}")

    async def iterate_prd(
        self,
        requirement_spec: Dict[str, Any],
        current_prd: str,
        change_request: Dict[str, Any],
        model_config: Optional[Dict[str, Any]] = None,
    ) -> str:
        user_prompt = f"""
最新 Requirement Spec：
{self.format_requirement_spec(requirement_spec)}

当前 PRD：
{current_prd}

结构化编辑指令：
{self.format_change_request(change_request)}
"""
        try:
            return self._chat(PRD_ITERATION_PROMPT, user_prompt, model_config=model_config)
        except Exception as exc:
            print(f"PRD iteration error: {exc}", file=sys.stderr)
            raise Exception(f"PRD 更新失败: {exc}")

    async def iterate_demo_html(
        self,
        requirement_spec: Dict[str, Any],
        current_demo_html: str,
        change_request: Dict[str, Any],
        model_config: Optional[Dict[str, Any]] = None,
    ) -> str:
        style_guidance = self.get_style_guidance(requirement_spec.get("style_preference"))
        user_prompt = f"""
最新 Requirement Spec：
{self.format_requirement_spec(requirement_spec)}

当前 Demo HTML：
{current_demo_html}

结构化编辑指令：
{self.format_change_request(change_request)}

{style_guidance}
"""
        try:
            html = self._chat(DEMO_ITERATION_PROMPT, user_prompt, model_config=model_config)
            cleaned = self._clean_code_fence(html)
            return self._complete_html_if_needed(cleaned, model_config=model_config)
        except Exception as exc:
            print(f"Demo iteration error: {exc}", file=sys.stderr)
            raise Exception(f"Demo 更新失败: {exc}")

    def _contains_phrase(self, haystack: str, phrase: str) -> bool:
        return bool(phrase) and self._normalize_text(phrase) in self._normalize_text(haystack)

    def _match_items(self, expected_items: List[str], *sources: str) -> Tuple[List[str], List[str]]:
        matched = []
        missing = []
        joined_source = "\n".join(filter(None, sources))
        for item in expected_items:
            if self._contains_phrase(joined_source, item):
                matched.append(item)
            else:
                missing.append(item)
        return matched, missing

    def _ratio_status(self, matched: List[str], expected: List[str]) -> str:
        if not expected:
            return "pass"
        ratio = len(matched) / max(len(expected), 1)
        if ratio >= 0.8:
            return "pass"
        if ratio >= 0.4:
            return "warning"
        return "fail"

    def _extract_markdown_headings(self, markdown_text: str) -> List[str]:
        return [match.strip() for match in re.findall(r"^#+\s+(.+)$", markdown_text or "", re.MULTILINE)]

    def _extract_demo_labels(self, demo_html: str) -> List[str]:
        stripped = re.sub(r"<script[\s\S]*?</script>", " ", demo_html or "", flags=re.IGNORECASE)
        stripped = re.sub(r"<style[\s\S]*?</style>", " ", stripped, flags=re.IGNORECASE)
        labels = re.findall(r">\s*([^<>]{1,80}?)\s*<", stripped)
        return [label.strip() for label in labels if label.strip()]

    def _build_check(self, check_id: str, label: str, status: str, summary: str, matched: List[str], missing: List[str]) -> Dict[str, Any]:
        return {
            "id": check_id,
            "label": label,
            "status": status,
            "summary": summary,
            "matched": matched,
            "missing": missing,
        }

    def check_consistency(
        self,
        requirement_spec: Dict[str, Any],
        prd: str,
        demo_html: str,
        prototype_outline: str,
    ) -> Dict[str, Any]:
        spec = self._normalize_spec(requirement_spec, requirement_spec)
        demo_labels = self._extract_demo_labels(demo_html)
        demo_source = "\n".join([demo_html, prototype_outline, *demo_labels])
        prd_headings = self._extract_markdown_headings(prd)
        prd_source = "\n".join([prd, *prd_headings])

        checks = []
        issues = []
        repair_suggestions: List[str] = []

        matched_pages, missing_pages = self._match_items(spec["primary_pages"], demo_source)
        page_status = self._ratio_status(matched_pages, spec["primary_pages"])
        checks.append(
            self._build_check(
                "page_coverage",
                "页面覆盖",
                page_status,
                f"已覆盖 {len(matched_pages)}/{len(spec['primary_pages'])} 个主要页面。",
                matched_pages,
                missing_pages,
            )
        )
        if missing_pages:
            issues.append(
                {
                    "title": "Demo 页面覆盖不足",
                    "severity": "high" if page_status == "fail" else "medium",
                    "description": f"以下主要页面尚未在 Demo 或原型说明中体现：{', '.join(missing_pages)}。",
                }
            )
            repair_suggestions.append(f"在 Demo 中补齐这些主要页面，并让它们进入主流程：{', '.join(missing_pages)}。")

        matched_features_prd, missing_features_prd = self._match_items(spec["key_features"], prd_source)
        matched_features_demo, missing_features_demo = self._match_items(spec["key_features"], demo_source)
        feature_missing = [item for item in spec["key_features"] if item in missing_features_prd or item in missing_features_demo]
        feature_matched = [item for item in spec["key_features"] if item not in feature_missing]
        feature_status = self._ratio_status(feature_matched, spec["key_features"])
        checks.append(
            self._build_check(
                "feature_coverage",
                "功能覆盖",
                feature_status,
                f"PRD 与 Demo 共同覆盖 {len(feature_matched)}/{len(spec['key_features'])} 个关键功能。",
                feature_matched,
                feature_missing,
            )
        )
        if feature_missing:
            issues.append(
                {
                    "title": "功能描述与页面表现不一致",
                    "severity": "high" if feature_status == "fail" else "medium",
                    "description": f"以下关键功能未同时出现在 PRD 与 Demo 中：{', '.join(feature_missing)}。",
                }
            )
            repair_suggestions.append(f"让 PRD 与 Demo 同步覆盖这些关键功能：{', '.join(feature_missing)}。")

        flow_signals = sum(
            1
            for pattern in [r"onclick=", r"addEventListener", r"data-view", r"show[A-Z]", r"classList", r"currentStep", r"activeView"]
            if re.search(pattern, demo_html or "", re.IGNORECASE)
        )
        flow_status = "pass" if flow_signals >= 3 and len(matched_pages) >= 2 else "warning" if flow_signals >= 2 else "fail"
        flow_missing = [] if flow_status == "pass" else ["关键页面之间的跳转或状态切换"]
        checks.append(
            self._build_check(
                "flow_connectivity",
                "流程连通",
                flow_status,
                "已检查 Demo 是否包含可点击主线、视图切换和结果反馈。",
                [f"检测到 {flow_signals} 个交互信号"],
                flow_missing,
            )
        )
        if flow_status != "pass":
            issues.append(
                {
                    "title": "Demo 主流程不够连通",
                    "severity": "high" if flow_status == "fail" else "medium",
                    "description": "Demo 中主要页面之间的跳转或状态切换不足，难以支撑完整演示。",
                }
            )
            repair_suggestions.append("为首页、核心任务页和结果页补齐可点击主线，确保按钮点击后能进入下一步视图。")

        naming_items = spec["primary_pages"] + spec["key_features"]
        matched_naming_outline, _ = self._match_items(naming_items, prototype_outline)
        matched_naming_prd, _ = self._match_items(naming_items, prd_source)
        naming_matched = [item for item in naming_items if item in matched_naming_outline and item in matched_naming_prd]
        naming_missing = [item for item in naming_items if item not in naming_matched]
        naming_status = self._ratio_status(naming_matched, naming_items)
        checks.append(
            self._build_check(
                "naming_consistency",
                "命名一致",
                naming_status,
                f"PRD 与原型说明共同保持了 {len(naming_matched)}/{len(naming_items)} 个核心名称的一致性。",
                naming_matched,
                naming_missing,
            )
        )
        if naming_missing:
            issues.append(
                {
                    "title": "命名未完全统一",
                    "severity": "medium",
                    "description": f"这些页面或功能名称在 PRD / 原型说明中不够一致：{', '.join(naming_missing)}。",
                }
            )
            repair_suggestions.append("统一 PRD、原型说明和 Demo 中的页面名、功能名和状态名，避免同义混用。")

        outline_reference = spec["primary_pages"] + spec["core_scenarios"]
        matched_outline, missing_outline = self._match_items(outline_reference, prototype_outline, demo_source)
        outline_status = self._ratio_status(matched_outline, outline_reference)
        checks.append(
            self._build_check(
                "prototype_alignment",
                "原型一致",
                outline_status,
                f"原型说明覆盖了 {len(matched_outline)}/{len(outline_reference)} 个页面或场景。",
                matched_outline,
                missing_outline,
            )
        )
        if missing_outline:
            issues.append(
                {
                    "title": "原型说明覆盖不足",
                    "severity": "medium",
                    "description": f"这些页面或场景没有在原型说明中清楚体现：{', '.join(missing_outline)}。",
                }
            )
            repair_suggestions.append("在原型说明中补充页面结构、操作路径和验证目标，覆盖遗漏的核心场景。")

        matched_scenarios, missing_scenarios = self._match_items(spec["core_scenarios"], prd_source, prototype_outline)
        scenario_status = self._ratio_status(matched_scenarios, spec["core_scenarios"])
        checks.append(
            self._build_check(
                "scenario_coverage",
                "场景缺失",
                scenario_status,
                f"核心场景已在评审材料中体现 {len(matched_scenarios)}/{len(spec['core_scenarios'])} 项。",
                matched_scenarios,
                missing_scenarios,
            )
        )
        if missing_scenarios:
            issues.append(
                {
                    "title": "核心场景存在遗漏",
                    "severity": "medium",
                    "description": f"这些核心场景尚未在 PRD 或原型说明中展开：{', '.join(missing_scenarios)}。",
                }
            )
            repair_suggestions.append(f"在 PRD 和原型说明中补充这些核心场景的验证方式：{', '.join(missing_scenarios)}。")

        weights = {
            "pass": 1.0,
            "warning": 0.55,
            "fail": 0.0,
        }
        score = round(sum(weights[item["status"]] for item in checks) / max(len(checks), 1) * 100)
        overall_level = "high" if score >= 85 else "medium" if score >= 60 else "low"

        deduped_suggestions = []
        seen = set()
        for suggestion in repair_suggestions:
            if suggestion not in seen:
                deduped_suggestions.append(suggestion)
                seen.add(suggestion)

        return {
            "overall_level": overall_level,
            "score": score,
            "checks": checks,
            "issues": issues,
            "repair_suggestions": deduped_suggestions,
        }

    def build_change_metadata(self, change_request: Dict[str, Any], requirement_spec: Dict[str, Any]) -> Dict[str, Any]:
        change_type = (change_request.get("change_type") or "").strip()
        change_label = CHANGE_TYPE_LABELS.get(change_type, "定点修改")
        target_module = (change_request.get("target_module") or "未指定模块").strip()
        affected_pages = change_request.get("affected_pages") or []
        changed_sections = CHANGE_SECTION_HINTS.get(change_type, ["关键模块", "用户操作路径"])

        if not affected_pages and change_type == "add_page":
            affected_pages = requirement_spec.get("primary_pages", [])[-1:]

        page_text = f"，涉及页面：{', '.join(affected_pages)}" if affected_pages else ""
        change_summary = f"已按“{change_label}”更新 {target_module}{page_text}。"

        return {
            "change_summary": change_summary,
            "changed_sections": changed_sections,
            "affected_pages": affected_pages,
        }


_llm_service = None


def get_llm_service() -> LLMService:
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service

