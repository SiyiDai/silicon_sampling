from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.request
from functools import lru_cache
from pathlib import Path
from typing import Any, Mapping


MODEL_NAME = "gpt-5.1"
API_URL = "https://api.openai.com/v1/chat/completions"
PROJECT_ROOT = Path(__file__).resolve().parents[1]
REAL_INDIVIDUAL_PIPELINE = PROJECT_ROOT / "real_individual_pipeline"
PROJECT_SITE_PACKAGES = PROJECT_ROOT / "silicon_sampling_env" / "Lib" / "site-packages"


def _load_project_api_key() -> str | None:
    for path in (REAL_INDIVIDUAL_PIPELINE, PROJECT_SITE_PACKAGES):
        if path.exists() and str(path) not in sys.path:
            sys.path.insert(0, str(path))
    try:
        from get_api_key import get_api_key  # type: ignore

        return get_api_key()
    except Exception:
        return os.environ.get("OPENAI_API_KEY")


@lru_cache(maxsize=1)
def get_client():
    api_key = _load_project_api_key()
    if not api_key:
        raise RuntimeError("No OpenAI API key found. Use real_individual_pipeline/get_api_key.py or OPENAI_API_KEY.")
    return HttpChatClient(api_key=api_key)


class _Message:
    def __init__(self, content: str):
        self.content = content


class _Choice:
    def __init__(self, content: str):
        self.message = _Message(content)


class HttpChatResponse:
    def __init__(self, body: Mapping[str, Any]):
        self.body = dict(body)
        choices = body.get("choices", [])
        content = ""
        if choices:
            try:
                content = choices[0]["message"]["content"] or ""
            except Exception:
                content = ""
        self.choices = [_Choice(content)]
        self.usage = body.get("usage", {})


class _Completions:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def create(
        self,
        *,
        model: str,
        messages: list[dict[str, str]],
        max_completion_tokens: int,
        temperature: float | None = None,
    ) -> HttpChatResponse:
        payload: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "max_completion_tokens": max_completion_tokens,
        }
        if temperature is not None:
            payload["temperature"] = temperature

        def request_once(body: dict[str, Any]) -> HttpChatResponse:
            data = json.dumps(body, ensure_ascii=False).encode("utf-8")
            request = urllib.request.Request(
                API_URL,
                data=data,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                method="POST",
            )
            with urllib.request.urlopen(request, timeout=180) as response:
                return HttpChatResponse(json.loads(response.read().decode("utf-8")))

        try:
            return request_once(payload)
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            if temperature is not None and "temperature" in body.lower():
                payload.pop("temperature", None)
                return request_once(payload)
            raise RuntimeError(f"OpenAI API error {exc.code}: {body[:1200]}") from exc


class _Chat:
    def __init__(self, api_key: str):
        self.completions = _Completions(api_key)


class HttpChatClient:
    def __init__(self, api_key: str):
        self.chat = _Chat(api_key)


PROFILE_SYSTEM_PROMPT = (
    "你是一位资深定性研究员和人物画像写作者，正在为肥胖患者购买流程市场研究创建一个真实、鲜活但严格受数据约束的中国受访者persona。"
    "请先把CFPS清洗样本中的硬事实转化为一个会呼吸的普通人：有生活处境、身体感受、就医与支付压力、信息渠道、减重经历倾向和治疗态度。"
    "必须守住硬事实：性别、年龄、身高、体重、BMI、BMI分层、学历、收入近似、疾病/合并症、就医和支付线索不得被改写。"
    "问卷要求但CFPS person文件不可直接判断的内容，只能作为有边界的模拟推断，并必须写入questionnaire_assumptions。"
    "若提供竞品或产品背景，它只能影响信息环境、治疗机制理解和品牌语境，不能改变受访者的事实条件。"
    "输出必须是JSON。"
)


QUESTIONNAIRE_SYSTEM_PROMPT = (
    "你现在要完全代入刚刚创建的同一位persona，像真实受访者一样填写肥胖患者购买流程问卷。"
    "请严格依据CFPS种子信息、persona、问卷题目、选项编码、show_if逻辑和validation要求作答。"
    "这是市场研究模拟，不是医学建议；不要输出医疗建议。"
    "必须保持年龄性别、BMI、合并症、减重旅程、GLP-1认知/使用、购药渠道、停药/换药、品牌评价和新产品评价前后一致。"
    "硬事实不得改变；不可直接判定字段可以合理模拟，但要在assumption_notes说明。"
    "只输出JSON，不要解释。"
)


_JSON_OBJECT_RE = re.compile(r"\{.*\}", re.DOTALL)


def parse_json_object(content: str, default: dict[str, Any] | None = None) -> dict[str, Any]:
    default = default or {}
    text = (content or "").strip()
    if not text:
        return default
    try:
        parsed = json.loads(text)
        return parsed if isinstance(parsed, dict) else default
    except json.JSONDecodeError:
        match = _JSON_OBJECT_RE.search(text)
        if not match:
            return default
        try:
            parsed = json.loads(match.group(0))
            return parsed if isinstance(parsed, dict) else default
        except json.JSONDecodeError:
            return default


def safe_int(value: object) -> int:
    try:
        return int(value or 0)
    except Exception:
        return 0


def extract_usage(response: object) -> dict[str, int]:
    usage = getattr(response, "usage", None)
    if usage is None and isinstance(response, Mapping):
        usage = response.get("usage")
    if usage is None:
        return {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
    if isinstance(usage, Mapping):
        prompt = safe_int(usage.get("prompt_tokens"))
        completion = safe_int(usage.get("completion_tokens"))
        total = safe_int(usage.get("total_tokens"))
    else:
        prompt = safe_int(getattr(usage, "prompt_tokens", 0))
        completion = safe_int(getattr(usage, "completion_tokens", 0))
        total = safe_int(getattr(usage, "total_tokens", 0))
    if total <= 0:
        total = prompt + completion
    return {"prompt_tokens": prompt, "completion_tokens": completion, "total_tokens": total}


def background_prompt_block(background_context: str) -> str:
    if not background_context.strip():
        return (
            "背景信息版本：不提供额外竞品/产品背景。\n"
            "请只使用CFPS种子、persona和问卷文本；品牌认知缺口按普通受访者的保守认知处理。\n\n"
        )
    return (
        "背景信息版本：提供以下竞品/产品背景给persona参考。\n"
        "使用规则：背景只影响信息环境和品牌/机制认知，不得改写CFPS硬事实、筛选条件、疾病线索或收入/BMI/年龄。\n"
        "背景内容：\n"
        f"{background_context.strip()}\n\n"
    )


def build_profile_user_prompt(individual_id: str, seed_context: str, background_context: str = "") -> str:
    return (
        f"Individual ID / 受访者ID：{individual_id}\n\n"
        f"CFPS种子信息与筛选边界：\n{seed_context}\n\n"
        f"{background_prompt_block(background_context)}"
        "请先写出一个鲜活、具体、可代入的中文persona，用于后续模拟填写问卷。\n"
        "画像要像真实受访者，而不是字段列表；但所有事实必须从种子信息或明确模拟推断而来。\n\n"
        "返回JSON字段：\n"
        "- individual_summary: 180-280字中文人物画像，写出生活处境、体重困扰、健康压力、支付能力、就医/信息习惯\n"
        "- response_style: 1-2句，描述此人填问卷时的心理和作答方式\n"
        "- stable_patterns: 5-8条稳定偏好/行为倾向\n"
        "- screening_facts: 结构化复述年龄、性别、BMI、学历、收入近似、合并症等硬事实\n"
        "- questionnaire_assumptions: 对城市线级、家庭总收入、既往减重措施、GLP-1经历、品牌/渠道等不可判定项的模拟推断及依据\n"
        "- unknown_fields_to_simulate: 数组，列出必须在问卷中模拟推断的字段\n"
        "- background_used: 布尔值\n"
        "只输出JSON。"
    )


def build_individual_profile_text(individual: Mapping[str, object]) -> str:
    summary = str(individual.get("individual_summary") or individual.get("persona_summary") or "").strip()
    response_style = str(individual.get("response_style", "")).strip()
    stable_patterns = individual.get("stable_patterns", [])
    assumptions = individual.get("questionnaire_assumptions", {})
    screening_facts = individual.get("screening_facts", {})

    lines: list[str] = []
    if summary:
        lines.append(f"Persona summary: {summary}")
    if response_style:
        lines.append(f"Response style: {response_style}")
    if stable_patterns:
        if isinstance(stable_patterns, list):
            lines.append("Stable patterns: " + "；".join(str(item).strip() for item in stable_patterns if str(item).strip()))
        else:
            lines.append(f"Stable patterns: {stable_patterns}")
    if screening_facts:
        lines.append("Screening facts: " + json.dumps(screening_facts, ensure_ascii=False))
    if assumptions:
        lines.append("Questionnaire assumptions: " + json.dumps(assumptions, ensure_ascii=False))
    return "\n".join(lines).strip() or "No persona profile available."


def generate_individual_with_meta(
    individual_id: str,
    seed_context: str,
    background_context: str = "",
    model: str = MODEL_NAME,
    max_completion_tokens: int = 1200,
    temperature: float | None = 0.6,
) -> dict[str, object]:
    client = get_client()
    user_prompt = build_profile_user_prompt(individual_id, seed_context, background_context)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": PROFILE_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        max_completion_tokens=max_completion_tokens,
        temperature=temperature,
    )
    raw_content = response.choices[0].message.content or ""
    parsed = parse_json_object(raw_content, default={})
    return {
        "individual": parsed,
        "raw": raw_content,
        "system_prompt": PROFILE_SYSTEM_PROMPT,
        "user_prompt": user_prompt,
        "usage": extract_usage(response),
    }
