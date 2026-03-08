from __future__ import annotations

import json
import os
import re
from functools import lru_cache
from typing import Dict, Mapping

try:
    from get_api_key import get_api_key  # type: ignore
except Exception:
    def get_api_key() -> str | None:
        return os.environ.get("OPENAI_API_KEY")


MODEL_NAME = "gpt-5.1"


@lru_cache(maxsize=1)
def get_client():
    api_key = get_api_key()
    if not api_key:
        raise RuntimeError(
            "No OpenAI API key found. Provide get_api_key() or set OPENAI_API_KEY."
        )

    try:
        from openai import OpenAI as OpenAIClient  # type: ignore
        return OpenAIClient(api_key=api_key)
    except Exception:
        import openai  # type: ignore

        if hasattr(openai, "OpenAI"):
            return openai.OpenAI(api_key=api_key)

        raise RuntimeError(
            "Could not import a compatible OpenAI client. Check your openai package installation."
        )


PERSONA_SYSTEM_PROMPT = (
    "You are an expert survey researcher and persona writer. "
    "Your job is to infer a concise but vivid respondent persona from a very small set "
    "of survey answers. Stay grounded in the provided answers. You may infer tendencies, "
    "motivations, and habits, but do not invent precise facts that are unsupported. "
    "The persona should sound like a believable human profile, not like a list of survey values."
)


ANSWER_SYSTEM_PROMPT = (
    "You are role-playing a survey respondent persona reconstructed from a few known answers. "
    "Answer the remaining survey questions exactly as this person would most likely answer. "
    "Be consistent with the persona and with the seed answers used to create it. "
    "When a question is clearly categorical or ordinal, return one plausible survey option or score, "
    "not an explanation. Keep each value short. Return JSON only."
)


_JSON_OBJECT_RE = re.compile(r"\{.*\}", re.DOTALL)


def _parse_json_object(content: str, default: Dict | None = None) -> Dict:
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


def build_persona_profile_text(persona: Mapping[str, object]) -> str:
    summary = str(persona.get("persona_summary", "")).strip()
    voice = str(persona.get("voice", "")).strip()
    traits = persona.get("traits", [])
    if not isinstance(traits, list):
        traits = []

    lines = []
    if summary:
        lines.append(f"Persona summary: {summary}")
    if voice:
        lines.append(f"Likely voice: {voice}")
    if traits:
        lines.append("Traits: " + ", ".join(str(item).strip() for item in traits if str(item).strip()))

    return "\n".join(lines).strip() or "No persona profile available."


def generate_persona(persona_id: str, persona_seed_context: str) -> Dict[str, object]:
    """
    Build a richer persona from the designated seed questions only.
    """
    client = get_client()
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": PERSONA_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"Persona ID: {persona_id}\n\n"
                    "Create a grounded respondent persona using ONLY the seed answers below.\n"
                    "Do not use any outside information.\n\n"
                    f"Seed answers:\n{persona_seed_context}\n\n"
                    "Return valid JSON with these keys:\n"
                    "- persona_summary: 90-160 words describing the respondent as a coherent person\n"
                    "- voice: 1-2 sentences capturing how this respondent tends to think or speak\n"
                    "- traits: array of 3-6 short trait phrases\n"
                    "Only return valid JSON."
                ),
            },
        ],
        max_completion_tokens=400,
        temperature=0.7,
    )

    content = response.choices[0].message.content or ""
    parsed = _parse_json_object(
        content,
        default={"persona_summary": "", "voice": "", "traits": []},
    )
    parsed["raw"] = content
    return parsed


def answer_questions_as_persona(
    persona_id: str,
    persona: Mapping[str, object],
    persona_seed_context: str,
    target_questions: Mapping[str, str],
) -> Dict[str, object]:
    """
    Ask the generated persona to answer the remaining survey questions.
    """
    client = get_client()
    persona_profile_text = build_persona_profile_text(persona)
    target_question_spec = "\n".join(
        f'- "{question_id}": {question_text}'
        for question_id, question_text in target_questions.items()
    )

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": ANSWER_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"Persona ID: {persona_id}\n\n"
                    f"Persona profile:\n{persona_profile_text}\n\n"
                    "Known seed answers used to build this persona:\n"
                    f"{persona_seed_context}\n\n"
                    "Answer the remaining survey questions below as this persona would most likely answer.\n"
                    "Use the question IDs exactly as provided.\n\n"
                    f"Questions to answer:\n{target_question_spec}\n\n"
                    "Return valid JSON with one top-level key:\n"
                    "- answers: an object mapping each question ID to a short answer\n"
                    "Only return valid JSON."
                ),
            },
        ],
        max_completion_tokens=700,
        temperature=0.4,
    )

    content = response.choices[0].message.content or ""
    parsed = _parse_json_object(content, default={"answers": {}})
    answers = parsed.get("answers", {})
    if not isinstance(answers, dict):
        answers = {}

    return {
        "answers": {key: str(value).strip() for key, value in answers.items()},
        "raw": content,
    }
