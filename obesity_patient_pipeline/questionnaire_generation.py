from __future__ import annotations

import argparse
import csv
import html
import importlib.util
import json
import random
import re
import sys
import time
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping
import xml.etree.ElementTree as ET

import pandas as pd

from context_generation import build_seed_context
from data_generation import (
    MODEL_NAME,
    QUESTIONNAIRE_SYSTEM_PROMPT,
    background_prompt_block,
    build_individual_profile_text,
    extract_usage,
    generate_individual_with_meta,
    get_client,
    parse_json_object,
)


PIPELINE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = PIPELINE_DIR.parent
DEFAULT_INPUT = PROJECT_ROOT / "data" / "persona_seed" / "肥胖患者210样本_清洗与EDA_中文" / "清洗后_210样本.csv"
DEFAULT_QUESTIONNAIRE_TEMPLATE = PROJECT_ROOT / "questionnaire" / "obesity_patient_questionnaire_template.py"
DEFAULT_BACKGROUND_FILE = Path(r"C:\Users\siyid\Downloads\Survo competitor.md")
DEFAULT_OUTPUT_DIR = PIPELINE_DIR / "data" / "obesity_questionnaire_10_persona_comparison"


def load_questionnaire_module(path: Path) -> Any:
    spec = importlib.util.spec_from_file_location("obesity_patient_questionnaire_template", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load questionnaire template: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def extract_docx_text(path: Path) -> str:
    with zipfile.ZipFile(path) as archive:
        xml_bytes = archive.read("word/document.xml")
    root = ET.fromstring(xml_bytes)
    namespace = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    paragraphs: list[str] = []
    for para in root.findall(".//w:p", namespace):
        parts = [node.text or "" for node in para.findall(".//w:t", namespace)]
        text = "".join(parts).strip()
        if text:
            paragraphs.append(text)
    return "\n".join(paragraphs)


def clean_markdown_background(text: str) -> str:
    text = html.unescape(text)
    replacements = {
        "\\-": "-",
        "\\+": "+",
        "\\(": "(",
        "\\)": ")",
        "\\.": ".",
        "\\_": "_",
        "\\/": "/",
        "\\>": ">",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    lines: list[str] = []
    previous_blank = False
    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        if not line.strip():
            if not previous_blank:
                lines.append("")
            previous_blank = True
            continue
        lines.append(line)
        previous_blank = False
    return "\n".join(lines).strip()


def markdown_background_to_narrative(text: str) -> str:
    """Turn the desk-research Markdown into persona-friendly Chinese prose."""
    cleaned = clean_markdown_background(text)
    if not cleaned:
        return ""
    heading_translations = {
        "Survo competitor": "Survodutide竞品背景",
        "**Desk research (pre-survey)**": "前期案头研究",
        "KTAs": "关键启发",
        "**Overview, by provider**": "按企业梳理",
        "**Medical investment, by mechanism**": "按机制梳理",
        "**Research second stage - Based on survey (in Chinese)**": "基于问卷资料的第二阶段中文整理",
    }
    narrative_lines: list[str] = []
    current_heading = ""
    for raw_line in cleaned.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        heading = line.lstrip("#").strip()
        if line.startswith("#") and heading:
            current_heading = heading_translations.get(heading, heading)
            narrative_lines.append(f"关于{current_heading}，这份资料提供了以下背景。")
            continue
        line = line.lstrip("-*").strip()
        if not re.search(r"[\u4e00-\u9fff]", line):
            continue
        line = line.replace("--&gt;", "，也就是说，").replace("-&gt;", "，也就是说，")
        line = line.replace("-->", "，也就是说，").replace("->", "，也就是说，")
        line = line.replace("&gt;", ">")
        line = line.rstrip("。.;；")
        if not line:
            continue
        narrative_lines.append(f"{line}。")
    return "\n".join(narrative_lines)


def organize_background_context(raw_text: str, source_name: str) -> str:
    narrative = markdown_background_to_narrative(raw_text)
    if not narrative:
        return ""
    return (
        f"【背景资料来源】{source_name}\n\n"
        "【给persona的中文叙述说明】\n"
        "这份材料不是受访者自己的病史，也不是医生给出的处方建议，而是访谈前让受访者理解竞品和机制差异的背景说明。"
        "作答时，persona可以像真实患者一样只吸收其中一部分信息：教育程度较高、信息渠道更主动的人可能更能理解GLP-1、GIP和胰高糖素的差别；"
        "对医疗信息不敏感的人则可能只记住“控制食欲、每周注射、减重幅度、副作用、是否覆盖脂肪肝/MASH”等直观信息。"
        "背景不能改变CFPS中的年龄、性别、BMI、收入、合并症和就医线索，也不能让所有人机械地偏好同一产品。\n\n"
        "机制上，GLP-1类药物通常通过增加饱腹感、降低食欲、延缓胃排空，并在血糖升高时促进胰岛素分泌来帮助体重和代谢管理。"
        "GIP相关机制更偏向胰岛素敏感性和葡萄糖代谢控制，常让受访者联想到糖尿病或代谢控制。"
        "胰高糖素机制在与GLP-1联合时，会被解释为可能增加能量消耗、促进脂肪代谢并帮助改善肝脏脂肪，因此更容易让有脂肪肝、MASH或代谢健康焦虑的人产生兴趣。"
        "资料中也提示，Mazdutide和Survodutide都强调食欲控制之外的能量消耗；Survodutide更容易被理解为偏代谢健康和脂肪肝/MASH方向，"
        "Mazdutide更容易被理解为偏体重、外观和综合减重方向。\n\n"
        "【整理后的背景叙述】\n"
        f"{narrative}"
    )


def load_background_text(path_text: str | None, max_chars: int) -> str:
    if not path_text:
        return ""
    path = Path(path_text)
    if not path.exists():
        raise FileNotFoundError(f"Background file not found: {path}")
    text = extract_docx_text(path) if path.suffix.lower() == ".docx" else path.read_text(encoding="utf-8")
    text = organize_background_context(text, path.name)
    if max_chars > 0 and len(text) > max_chars:
        return text[:max_chars].rstrip() + "\n[背景信息因长度限制已截断]"
    return text


def compact_json(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def clean_value(value: Any) -> str:
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except Exception:
        pass
    if isinstance(value, float):
        if value.is_integer():
            return str(int(value))
        return f"{value:.4f}".rstrip("0").rstrip(".")
    return str(value).strip()


def select_random_personas(df: pd.DataFrame, limit: int, seed: int) -> pd.DataFrame:
    if limit <= 0:
        raise ValueError("--limit must be positive")
    if len(df) < limit:
        raise ValueError(f"Not enough rows to sample {limit}; only {len(df)} rows available.")
    selected = df.sample(n=limit, random_state=seed).copy()
    return selected.sort_values("样本编号").reset_index(drop=True) if "样本编号" in selected.columns else selected.reset_index(drop=True)


def question_ids(qnr_module: Any, include_screening: bool) -> list[str]:
    specs = qnr_module.QUESTIONNAIRE if include_screening else tuple(
        spec for spec in qnr_module.QUESTIONNAIRE if spec.section != "甄别问卷" and spec.qid != "CONSENT"
    )
    return [spec.qid for spec in specs]


EXPORT_SOURCE_QID = {
    "A6": "A6",
    "A6a": "A6",
    "A6b": "A6",
    "A14": "A14_A15",
    "A15": "A14_A15",
    "C4": "C4_C5",
    "C5": "C4_C5",
}

NON_MEDICAL_METHOD_CODES = [str(i) for i in range(1, 12)]
NAME_TEST_CODES = [str(i) for i in range(1, 7)]
CORE_GLP1_BRAND_CODES = {"3", "4", "5", "6"}


def export_question_ids(qnr_module: Any, include_screening: bool) -> list[str]:
    expanded: list[str] = []
    for qid in question_ids(qnr_module, include_screening):
        if qid == "A6":
            expanded.extend(["A6", "A6a", "A6b"])
        elif qid == "A14_A15":
            expanded.extend(["A14", "A15"])
        elif qid == "C4_C5":
            expanded.extend(["C4", "C5"])
        else:
            expanded.append(qid)

    # Match the desired questionnaire export order: B10/B11 should appear before B12.
    for qid in ("B10", "B11"):
        if qid in expanded and "B12" in expanded:
            expanded.remove(qid)
            expanded.insert(expanded.index("B12"), qid)
    return expanded


def as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def code_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value).strip()


def code_set(value: Any) -> set[str]:
    if isinstance(value, (list, tuple, set)):
        return {code_text(item) for item in value if code_text(item)}
    if value in (None, ""):
        return set()
    return {code_text(value)}


def answer_contains(answers: Mapping[str, Any], qid: str, code: object) -> bool:
    return str(code) in code_set(answers.get(qid))


def is_empty_answer(value: Any) -> bool:
    return value is None or value == "" or value == [] or value == {}


def b9_used_codes(answers: Mapping[str, Any]) -> set[str]:
    rows = as_mapping(answers.get("B9"))
    used: set[str] = set()
    for code, payload in rows.items():
        item = as_mapping(payload)
        if code_text(item.get("used")) == "1":
            used.add(code_text(code))
    return used


def b9_stopped_codes(answers: Mapping[str, Any]) -> set[str]:
    rows = as_mapping(answers.get("B9"))
    stopped: set[str] = set()
    for code, payload in rows.items():
        item = as_mapping(payload)
        if code_text(item.get("used")) == "1" and code_text(item.get("status")) == "2":
            stopped.add(code_text(code))
    return stopped


def b9_current_codes(answers: Mapping[str, Any]) -> set[str]:
    rows = as_mapping(answers.get("B9"))
    current: set[str] = set()
    for code, payload in rows.items():
        item = as_mapping(payload)
        if code_text(item.get("used")) == "1" and code_text(item.get("status")) == "1":
            current.add(code_text(code))
    return current


def has_glp1_experience(answers: Mapping[str, Any]) -> bool:
    return answer_contains(answers, "S10", 13) or answer_contains(answers, "A20", 2)


def is_question_applicable(source_qid: str, answers: Mapping[str, Any]) -> bool:
    if source_qid == "CONSENT":
        return True
    if code_text(answers.get("CONSENT") or "1") == "2":
        return False
    if source_qid == "S9":
        return answer_contains(answers, "S8", 1)
    if source_qid == "A6":
        return bool(code_set(answers.get("S10")) & set(NON_MEDICAL_METHOD_CODES))
    if source_qid == "A10":
        return not answer_contains(answers, "A9", 1)
    if source_qid == "A11":
        return answer_contains(answers, "A9", 1)
    if source_qid in {"A12", "A13"}:
        return code_text(answers.get("A11")) == "1"
    if source_qid in {"A14_A15", "A16", "A17"}:
        return code_text(answers.get("A11")) == "2"
    if source_qid == "A18":
        return answer_contains(answers, "A9", 2)
    if source_qid == "A19":
        return answer_contains(answers, "A9", 2) and not answer_contains(answers, "A9", 1)
    if source_qid == "A19a":
        return code_text(answers.get("A19")) == "1"
    if source_qid == "A20":
        return code_text(answers.get("A11")) in {"1", "2"} or code_text(answers.get("A19")) == "1"
    if source_qid == "A21":
        return answer_contains(answers, "A20", 2)
    if source_qid == "A22":
        return answer_contains(answers, "A20", 4)
    if source_qid == "A23a":
        return code_text(answers.get("A23")) == "1"
    if source_qid == "B1":
        return not has_glp1_experience(answers)
    if source_qid == "B2":
        return code_text(answers.get("B1")) == "1"
    if source_qid == "B8":
        return answer_contains(answers, "S10", 13) and not answer_contains(answers, "A9", 1)
    if source_qid == "B9":
        return has_glp1_experience(answers)
    if source_qid in {"B12", "B13", "B14", "B14d", "B15", "B19", "B20", "B23"}:
        return bool(b9_used_codes(answers) & CORE_GLP1_BRAND_CODES)
    if source_qid in {"B10", "B18"}:
        return bool(b9_stopped_codes(answers))
    if source_qid == "B11":
        return len(b9_used_codes(answers)) >= 2
    if source_qid == "B15a":
        rows = as_mapping(answers.get("B15"))
        return any(code_text(as_mapping(item).get("interrupted")) == "1" for item in rows.values())
    if source_qid == "B16":
        return bool(b9_used_codes(answers) & {"3", "4", "5"})
    if source_qid == "B17":
        return has_glp1_experience(answers)
    if source_qid in {"B20a", "B21", "B22"}:
        return any(code_text(item) == "2" for item in as_mapping(answers.get("B20")).values())
    if source_qid == "B23a":
        return any("2" in code_set(item) for item in as_mapping(answers.get("B23")).values())
    if source_qid == "B24":
        used = b9_used_codes(answers)
        return bool(used) and not b9_current_codes(answers)
    if source_qid == "B24a":
        return code_text(answers.get("B24")) == "1"
    if source_qid == "B24b":
        return code_text(answers.get("B24a")) in {"1", "2", "3", "4"}
    if source_qid == "C3":
        try:
            return float(answers.get("C2")) < 8
        except Exception:
            return False
    if source_qid == "D2":
        return code_text(answers.get("D1")) in {"1", "2"}
    if source_qid == "D5":
        return code_text(answers.get("D4")) in {"2", "3", "4"}
    if source_qid == "D9":
        d8 = as_mapping(answers.get("D8"))
        try:
            return float(d8.get("4")) > 5
        except Exception:
            return False
    return True


def format_series(parts: list[str]) -> str:
    return ", ".join(parts)


def clean_numeric_for_series(value: Any) -> str:
    text = clean_value(value)
    if not text:
        return ""
    try:
        number = float(text)
    except Exception:
        return text
    if number.is_integer():
        return str(int(number))
    return f"{number:.1f}".rstrip("0").rstrip(".")


def format_a6_series(export_qid: str, answers: Mapping[str, Any]) -> str:
    if not is_question_applicable("A6", answers):
        return "NA"
    selected = code_set(answers.get("S10")) & set(NON_MEDICAL_METHOD_CODES)
    payload = as_mapping(answers.get("A6"))
    if not payload and selected:
        return ""
    metric = {"A6": "attempts", "A6a": "avg_months", "A6b": "monthly_cost_rmb"}[export_qid]
    attempt_metric = "attempts"
    parts: list[str] = []
    for code in NON_MEDICAL_METHOD_CODES:
        if code not in selected:
            parts.append("0")
            continue
        item = as_mapping(payload.get(code))
        if not item:
            parts.append("")
            continue
        attempts = clean_numeric_for_series(item.get(attempt_metric))
        if attempts == "0":
            parts.append("0")
            continue
        if export_qid in {"A6a", "A6b"} and not attempts:
            parts.append("")
            continue
        parts.append(clean_numeric_for_series(item.get(metric)))
    return format_series(parts)


def format_name_test_series(export_qid: str, answers: Mapping[str, Any]) -> str:
    payload = as_mapping(answers.get("C4_C5"))
    if not payload:
        return ""
    metric = "readability" if export_qid == "C4" else "memorability"
    return format_series(clean_numeric_for_series(as_mapping(payload.get(code)).get(metric)) for code in NAME_TEST_CODES)


def format_dual_department(export_qid: str, answers: Mapping[str, Any]) -> str:
    if not is_question_applicable("A14_A15", answers):
        return "NA"
    payload = as_mapping(answers.get("A14_A15"))
    if not payload:
        return ""
    key = "A14_first_department" if export_qid == "A14" else "A15_treatment_department"
    return clean_value(payload.get(key))


def format_answer_for_export(export_qid: str, answers: Mapping[str, Any]) -> str:
    source_qid = EXPORT_SOURCE_QID.get(export_qid, export_qid)
    if export_qid in {"A6", "A6a", "A6b"}:
        return format_a6_series(export_qid, answers)
    if export_qid in {"A14", "A15"}:
        return format_dual_department(export_qid, answers)
    if export_qid in {"C4", "C5"}:
        return format_name_test_series(export_qid, answers)
    if not is_question_applicable(source_qid, answers):
        return "NA"
    value = answers.get(source_qid)
    if is_empty_answer(value):
        return ""
    return compact_json(value)


def build_questionnaire_user_prompt(
    qnr_module: Any,
    individual_id: str,
    seed_context: str,
    profile: Mapping[str, Any],
    include_screening: bool,
    background_context: str,
) -> str:
    questionnaire_text = qnr_module.questionnaire_to_prompt_text(include_screening=include_screening)
    expected_shape = qnr_module.expected_answer_shape(include_screening=include_screening)
    profile_text = build_individual_profile_text(profile)
    return (
        f"Individual ID / 受访者ID：{individual_id}\n\n"
        f"CFPS种子信息与筛选边界：\n{seed_context}\n\n"
        f"第一阶段生成的persona：\n{profile_text}\n\n"
        f"{background_prompt_block(background_context)}"
        "现在请完全代入该persona填写问卷。必须遵守：\n"
        "- 使用题目ID作为answers的键，不要改题号。\n"
        "- 单选题返回一个代码；多选题返回代码数组；排序题返回{代码: 排名}；矩阵/数值题按answer_format返回。\n"
        "- CONSENT、S类甄别题必须与硬事实一致；S7 BMI必须与身高、体重、BMI种子一致。\n"
        "- 若题目有show_if，不符合条件的题目留空、空数组或空对象；导出CSV时这些题目会被标为NA，适用但未回答才会留空。\n"
        "- GLP-1相关题要保持完整时间线：知晓、尝试、当前/既往使用、品牌、渠道、剂量、停药/换药和未来意愿不能互相矛盾。\n"
        "- C部分为信息输入题，所有受访者在回答C1-C7前都必须阅读产品示卡文字，并以示卡中的产品X/A/B/C信息作为判断依据。\n"
        "- 背景信息只作为信息语境，不得让所有人机械偏好同一品牌。\n"
        "- 在assumption_notes写明哪些答案来自CFPS不可直接判定字段的模拟推断。\n"
        "- 在consistency_checks自检年龄、BMI、合并症、减重经历、GLP-1与购药/停药逻辑。\n\n"
        "输出JSON结构：\n"
        "{\n"
        '  "answers": {题目ID: 按题目要求的代码/数组/对象},\n'
        '  "assumption_notes": ["列出模拟推断及依据"],\n'
        '  "consistency_checks": ["列出关键逻辑自检结果"]\n'
        "}\n\n"
        "题目ID和答案格式参考：\n"
        f"{json.dumps(expected_shape, ensure_ascii=False, indent=2)}\n\n"
        f"{questionnaire_text}\n\n"
        "请仅输出JSON。"
    )


def answer_full_questionnaire_with_meta(
    qnr_module: Any,
    individual_id: str,
    individual: Mapping[str, Any],
    seed_context: str,
    include_screening: bool,
    background_context: str,
    model: str,
    max_completion_tokens: int,
    temperature: float | None,
) -> dict[str, Any]:
    client = get_client()
    user_prompt = build_questionnaire_user_prompt(
        qnr_module=qnr_module,
        individual_id=individual_id,
        seed_context=seed_context,
        profile=individual,
        include_screening=include_screening,
        background_context=background_context,
    )
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": QUESTIONNAIRE_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        max_completion_tokens=max_completion_tokens,
        temperature=temperature,
    )
    raw_content = response.choices[0].message.content or ""
    parsed = parse_json_object(raw_content, default={"answers": {}, "assumption_notes": [], "consistency_checks": []})
    answers = parsed.get("answers", {})
    if not isinstance(answers, Mapping):
        answers = {}
    return {
        "answers": dict(answers),
        "assumption_notes": parsed.get("assumption_notes", []),
        "consistency_checks": parsed.get("consistency_checks", []),
        "raw": raw_content,
        "system_prompt": QUESTIONNAIRE_SYSTEM_PROMPT,
        "user_prompt": user_prompt,
        "usage": extract_usage(response),
    }


def run_variant(
    *,
    qnr_module: Any,
    sample_df: pd.DataFrame,
    output_dir: Path,
    background_context: str,
    variant_label: str,
    include_screening: bool,
    model: str,
    profile_tokens: int,
    questionnaire_tokens: int,
    profile_temperature: float | None,
    questionnaire_temperature: float | None,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    ids = export_question_ids(qnr_module, include_screening)
    answer_fields = [
        "pid",
        "样本编号",
        "variant",
        "目标人群细分",
        "BMI配额段",
        "persona_summary",
        "response_style",
    ] + ids + ["assumption_notes", "consistency_checks", "status", "error"]
    log_fields = [
        "pid",
        "样本编号",
        "variant",
        "profile_seconds",
        "questionnaire_seconds",
        "profile_prompt_tokens",
        "profile_completion_tokens",
        "profile_total_tokens",
        "questionnaire_prompt_tokens",
        "questionnaire_completion_tokens",
        "questionnaire_total_tokens",
        "individual_total_tokens",
        "profile_system_prompt",
        "profile_user_prompt",
        "questionnaire_system_prompt",
        "questionnaire_user_prompt",
        "profile_raw_response",
        "questionnaire_raw_response",
        "status",
        "error",
    ]

    answers_path = output_dir / "answers.csv"
    log_path = output_dir / "logs.csv"
    jsonl_path = output_dir / "personas_and_answers.jsonl"
    prompt_template_path = output_dir / "questionnaire_prompt_template.txt"
    background_path = output_dir / "background_context.txt"
    prompt_template_path.write_text(qnr_module.questionnaire_to_prompt_text(include_screening=include_screening), encoding="utf-8")
    background_path.write_text(background_context, encoding="utf-8")

    total_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
    processed = 0
    failed = 0
    run_start = time.perf_counter()
    run_started_utc = datetime.now(timezone.utc).isoformat()

    with answers_path.open("w", newline="", encoding="utf-8-sig") as answer_file, log_path.open(
        "w", newline="", encoding="utf-8-sig"
    ) as log_file, jsonl_path.open("w", encoding="utf-8") as jsonl_file:
        answer_writer = csv.DictWriter(answer_file, fieldnames=answer_fields)
        log_writer = csv.DictWriter(log_file, fieldnames=log_fields)
        answer_writer.writeheader()
        log_writer.writeheader()

        for _, row in sample_df.iterrows():
            row_dict = row.to_dict()
            pid = clean_value(row_dict.get("个人ID_pid") or row_dict.get("样本编号"))
            sample_id = clean_value(row_dict.get("样本编号"))
            seed_context = build_seed_context(row_dict)
            profile_seconds = 0.0
            questionnaire_seconds = 0.0
            profile_raw = ""
            questionnaire_raw = ""
            profile_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
            questionnaire_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
            status = "ok"
            error = ""
            profile: dict[str, Any] = {}
            profile_bundle: dict[str, Any] = {}
            questionnaire_result: dict[str, Any] = {"answers": {}, "assumption_notes": [], "consistency_checks": []}

            try:
                start = time.perf_counter()
                profile_bundle = generate_individual_with_meta(
                    individual_id=pid,
                    seed_context=seed_context,
                    background_context=background_context,
                    model=model,
                    max_completion_tokens=profile_tokens,
                    temperature=profile_temperature,
                )
                profile_seconds = time.perf_counter() - start
                profile = profile_bundle.get("individual", {})
                if not isinstance(profile, dict):
                    profile = {}
                profile_raw = str(profile_bundle.get("raw", ""))
                profile_usage = profile_bundle.get("usage", profile_usage)
                if not isinstance(profile_usage, dict):
                    profile_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}

                start = time.perf_counter()
                questionnaire_result = answer_full_questionnaire_with_meta(
                    qnr_module=qnr_module,
                    individual_id=pid,
                    individual=profile,
                    seed_context=seed_context,
                    include_screening=include_screening,
                    background_context=background_context,
                    model=model,
                    max_completion_tokens=questionnaire_tokens,
                    temperature=questionnaire_temperature,
                )
                questionnaire_seconds = time.perf_counter() - start
                questionnaire_raw = str(questionnaire_result.get("raw", ""))
                questionnaire_usage = questionnaire_result.get("usage", questionnaire_usage)
                if not isinstance(questionnaire_usage, dict):
                    questionnaire_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
                processed += 1
            except Exception as exc:
                status = "failed"
                error = str(exc)
                failed += 1

            answers = questionnaire_result.get("answers", {})
            if not isinstance(answers, Mapping):
                answers = {}
            answer_row = {
                "pid": pid,
                "样本编号": sample_id,
                "variant": variant_label,
                "目标人群细分": clean_value(row_dict.get("目标人群细分")),
                "BMI配额段": clean_value(row_dict.get("BMI配额段")),
                "persona_summary": clean_value(profile.get("individual_summary") or profile.get("persona_summary")),
                "response_style": clean_value(profile.get("response_style")),
                "assumption_notes": compact_json(questionnaire_result.get("assumption_notes", [])),
                "consistency_checks": compact_json(questionnaire_result.get("consistency_checks", [])),
                "status": status,
                "error": error,
            }
            for qid in ids:
                answer_row[qid] = format_answer_for_export(qid, answers)
            answer_writer.writerow(answer_row)

            for usage in (profile_usage, questionnaire_usage):
                for key in total_usage:
                    total_usage[key] += int(usage.get(key, 0))
            individual_total_tokens = int(profile_usage.get("total_tokens", 0)) + int(questionnaire_usage.get("total_tokens", 0))
            log_writer.writerow(
                {
                    "pid": pid,
                    "样本编号": sample_id,
                    "variant": variant_label,
                    "profile_seconds": f"{profile_seconds:.4f}",
                    "questionnaire_seconds": f"{questionnaire_seconds:.4f}",
                    "profile_prompt_tokens": int(profile_usage.get("prompt_tokens", 0)),
                    "profile_completion_tokens": int(profile_usage.get("completion_tokens", 0)),
                    "profile_total_tokens": int(profile_usage.get("total_tokens", 0)),
                    "questionnaire_prompt_tokens": int(questionnaire_usage.get("prompt_tokens", 0)),
                    "questionnaire_completion_tokens": int(questionnaire_usage.get("completion_tokens", 0)),
                    "questionnaire_total_tokens": int(questionnaire_usage.get("total_tokens", 0)),
                    "individual_total_tokens": individual_total_tokens,
                    "profile_system_prompt": profile_bundle.get("system_prompt", ""),
                    "profile_user_prompt": profile_bundle.get("user_prompt", ""),
                    "questionnaire_system_prompt": questionnaire_result.get("system_prompt", ""),
                    "questionnaire_user_prompt": questionnaire_result.get("user_prompt", ""),
                    "profile_raw_response": profile_raw,
                    "questionnaire_raw_response": questionnaire_raw,
                    "status": status,
                    "error": error,
                }
            )
            jsonl_file.write(
                json.dumps(
                    {
                        "pid": pid,
                        "sample_id": sample_id,
                        "variant": variant_label,
                        "seed_context": seed_context,
                        "profile": profile,
                        "questionnaire": questionnaire_result,
                        "status": status,
                        "error": error,
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )

    summary = {
        "variant": variant_label,
        "background_included": bool(background_context.strip()),
        "background_chars": len(background_context),
        "run_started_utc": run_started_utc,
        "run_finished_utc": datetime.now(timezone.utc).isoformat(),
        "total_seconds": round(time.perf_counter() - run_start, 4),
        "processed": processed,
        "failed": failed,
        "question_count": len(ids),
        "total_usage": total_usage,
        "files": {
            "answers": str(answers_path),
            "logs": str(log_path),
            "personas_and_answers": str(jsonl_path),
            "prompt_template": str(prompt_template_path),
            "background_context": str(background_path),
        },
    }
    (output_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return summary


def process_questionnaire_comparison(
    *,
    input_file: str,
    output_dir: str,
    limit: int = 10,
    seed: int = 20260528,
    variants: str = "both",
    background_file: str | None = str(DEFAULT_BACKGROUND_FILE),
    background_max_chars: int = 12000,
    questionnaire_template: str = str(DEFAULT_QUESTIONNAIRE_TEMPLATE),
    include_screening: bool = True,
    model: str = MODEL_NAME,
    profile_tokens: int = 1200,
    questionnaire_tokens: int = 7000,
    profile_temperature: float | None = 0.6,
    questionnaire_temperature: float | None = 0.35,
) -> dict[str, Any]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    qnr_module = load_questionnaire_module(Path(questionnaire_template))
    df = pd.read_csv(input_file, encoding="utf-8-sig")
    sample_df = select_random_personas(df, limit=limit, seed=seed)
    sample_path = output_path / "selected_10_personas.csv"
    sample_df.to_csv(sample_path, index=False, encoding="utf-8-sig")

    if variants == "both":
        variant_plan = [("without_background", ""), ("with_background", "")]
    elif variants == "with-background":
        variant_plan = [("with_background", "")]
    else:
        variant_plan = [("without_background", "")]

    background_text = ""
    if any(label == "with_background" for label, _ in variant_plan):
        background_text = load_background_text(background_file, background_max_chars)

    summaries: list[dict[str, Any]] = []
    for label, _ in variant_plan:
        variant_dir = output_path / ("含背景信息" if label == "with_background" else "不含背景信息")
        context = background_text if label == "with_background" else ""
        summaries.append(
            run_variant(
                qnr_module=qnr_module,
                sample_df=sample_df,
                output_dir=variant_dir,
                background_context=context,
                variant_label=label,
                include_screening=include_screening,
                model=model,
                profile_tokens=profile_tokens,
                questionnaire_tokens=questionnaire_tokens,
                profile_temperature=profile_temperature,
                questionnaire_temperature=questionnaire_temperature,
            )
        )

    run_summary = {
        "run_started_date": datetime.now().isoformat(),
        "input_file": str(input_file),
        "output_dir": str(output_path),
        "selected_sample": str(sample_path),
        "limit": limit,
        "random_seed": seed,
        "variants": variants,
        "include_screening": include_screening,
        "model": model,
        "variant_summaries": summaries,
    }
    summary_path = output_path / "comparison_summary.json"
    summary_path.write_text(json.dumps(run_summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return run_summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate obesity questionnaire answers for sampled CFPS personas.")
    parser.add_argument("--input", default=str(DEFAULT_INPUT), help="Cleaned 210-person CSV.")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR), help="Output directory.")
    parser.add_argument("--limit", type=int, default=10, help="Random persona count.")
    parser.add_argument("--seed", type=int, default=20260528, help="Random selection seed.")
    parser.add_argument("--variants", choices=["both", "with-background", "without-background"], default="both")
    parser.add_argument("--background-file", default=str(DEFAULT_BACKGROUND_FILE))
    parser.add_argument("--background-max-chars", type=int, default=0, help="<=0 means include the full organized background.")
    parser.add_argument("--questionnaire-template", default=str(DEFAULT_QUESTIONNAIRE_TEMPLATE))
    parser.add_argument("--include-screening", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--model", default=MODEL_NAME)
    parser.add_argument("--profile-tokens", type=int, default=1200)
    parser.add_argument("--questionnaire-tokens", type=int, default=7000)
    parser.add_argument("--profile-temperature", type=float, default=0.6)
    parser.add_argument("--questionnaire-temperature", type=float, default=0.35)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    summary = process_questionnaire_comparison(
        input_file=args.input,
        output_dir=args.output_dir,
        limit=args.limit,
        seed=args.seed,
        variants=args.variants,
        background_file=args.background_file,
        background_max_chars=args.background_max_chars,
        questionnaire_template=args.questionnaire_template,
        include_screening=args.include_screening,
        model=args.model,
        profile_tokens=args.profile_tokens,
        questionnaire_tokens=args.questionnaire_tokens,
        profile_temperature=args.profile_temperature,
        questionnaire_temperature=args.questionnaire_temperature,
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
