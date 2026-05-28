from __future__ import annotations

import csv
import math
from pathlib import Path
from typing import Any, Mapping


SEED_COLUMNS = [
    "样本编号",
    "个人ID_pid",
    "年龄",
    "性别",
    "年龄配额段",
    "省份",
    "城乡属性",
    "城市线级配额",
    "学历",
    "受教育年限_插补",
    "收入筛选状态",
    "个人就业收入_元_家庭收入近似",
    "收入配额段_近似",
    "身高_cm",
    "体重_kg",
    "BMI",
    "BMI分层",
    "BMI配额段",
    "目标人群细分",
    "合并症类别汇总",
    "是否有糖尿病",
    "合并症_糖尿病",
    "合并症_高血压",
    "合并症_肝病或MASH线索",
    "合并症_心脑血管",
    "合并症_关节运动系统",
    "全部疾病名称",
    "自评健康",
    "健康变化",
    "两周内是否身体不适",
    "就医行为标签",
    "就诊机构层级",
    "医疗服务满意度简化",
    "医疗支出_元",
    "医疗支出分层",
    "自付医疗支出占比",
    "自付负担分层",
    "医保类型",
    "工作状态",
    "工作单位或职业类型",
    "锻炼频率",
    "锻炼时长_分钟",
    "运动频率级别",
    "筛选可判定结论",
    "可用字段匹配说明",
    "Persona生成线索",
]

MISSING_VALUE_MARKERS = {"", "nan", "na", "n/a", "null", "none", "<na>", "缺失", "不适用", "不可判定", "不判定"}

SurveyRow = dict[str, str]

HARD_FACT_COLUMNS = [
    "性别",
    "年龄",
    "年龄配额段",
    "身高_cm",
    "体重_kg",
    "BMI",
    "BMI配额段",
    "学历",
    "个人就业收入_元_家庭收入近似",
    "收入筛选状态",
    "合并症类别汇总",
    "全部疾病名称",
]

UNOBSERVABLE_QUESTIONNAIRE_FIELDS = [
    "城市线级：当前 person 文件只有省份/城乡和区域编号，缺少可严格映射到问卷城市线级的城市名。",
    "家庭总收入：当前使用个人就业收入 emp_income>=17000 作为严格近似代理，但不是家庭年收入。",
    "既往至少3种减重措施：CFPS person 文件没有完整减重措施史。",
    "GLP-1既往/当前使用经历、具体品牌、剂量滴定、停药/换药、购药渠道：CFPS person 文件没有直接字段。",
    "腰围、诊断分型、医生处方细节、品牌认知来源：需要在问卷作答阶段基于画像保守模拟。",
]


def _clean_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and math.isnan(value):
        return ""
    return str(value).replace("\n", " ").strip()


def _is_missing(value: Any) -> bool:
    return _clean_text(value).casefold() in MISSING_VALUE_MARKERS


def _clean_value(value: Any) -> str:
    if _is_missing(value):
        return ""
    if isinstance(value, float):
        if value.is_integer():
            return str(int(value))
        return f"{value:.4f}".rstrip("0").rstrip(".")
    return str(value).strip()


def _normalize_row(fieldnames: list[str], values: list[object]) -> SurveyRow:
    return {key: _clean_text(value) for key, value in zip(fieldnames, values)}


def read_survey_table(table_file: str) -> tuple[list[str], list[str], list[SurveyRow]]:
    """Read a standard-header CSV; returns fieldnames, labels, rows."""
    path = Path(table_file)
    if path.suffix.lower() != ".csv":
        raise ValueError(f"Only standard CSV input is supported for this pipeline: {path}")
    rows: list[SurveyRow] = []
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.reader(handle)
        fieldnames = [_clean_text(cell) for cell in next(reader, [])]
        labels = list(fieldnames)
        for values in reader:
            if not values or all(_is_missing(cell) for cell in values):
                continue
            rows.append(_normalize_row(fieldnames, values))
    return fieldnames, labels, rows


def load_survey_rows(table_file: str):
    fieldnames, labels, rows = read_survey_table(table_file)
    for row in rows:
        yield fieldnames, labels, row


def build_label_map(fieldnames: list[str], labels: list[str]) -> dict[str, str]:
    return {
        _clean_text(fieldname): _clean_text(label) or _clean_text(fieldname)
        for fieldname, label in zip(fieldnames, labels)
        if _clean_text(fieldname)
    }


def build_seed_context(row: Mapping[str, Any]) -> str:
    """Build the grounded Chinese seed context used for profile and questionnaire prompts."""
    hard_fact_lines = []
    for col in HARD_FACT_COLUMNS:
        value = _clean_value(row.get(col))
        if value:
            hard_fact_lines.append(f"- {col}: {value}")

    seed_lines = []
    for col in SEED_COLUMNS:
        value = _clean_value(row.get(col))
        if value:
            seed_lines.append(f"- {col}: {value}")

    observable_notes = [
        "严格筛选口径（不要在问卷作答中改写）：",
        "- 年龄落入问卷年龄段。",
        "- 有效身高体重并计算 BMI，且 BMI>24。",
        "- 学历为高中/中专及以上。",
        "- 家庭年收入要求在 person 文件中用个人就业收入 emp_income>=17000 作严格近似代理。",
        "- 若 24<BMI<=28，必须存在问卷列举合并症在 CFPS 疾病编码中的可识别近似线索；不使用任意疾病编码放宽。",
        "- 城市线级、既往3种以上减重措施和GLP-1经历不可直接判定，不是筛选放宽项。",
    ]

    parts = [
        "已知硬事实（回答问卷时不得改变）：",
        "\n".join(hard_fact_lines) if hard_fact_lines else "- 无",
        "",
        "CFPS清洗后种子字段：",
        "\n".join(seed_lines) if seed_lines else "- 无",
        "",
        "\n".join(observable_notes),
        "",
        "问卷中需要模拟推断、但必须与硬事实一致的字段：",
        "\n".join(f"- {item}" for item in UNOBSERVABLE_QUESTIONNAIRE_FIELDS),
    ]
    return "\n".join(parts)


def build_persona_seed_context(
    row: Mapping[str, Any],
    label_map: Mapping[str, str] | None = None,
    persona_keys: list[str] | None = None,
) -> str:
    """Compatibility alias matching real_individual_pipeline."""
    return build_seed_context(row)

