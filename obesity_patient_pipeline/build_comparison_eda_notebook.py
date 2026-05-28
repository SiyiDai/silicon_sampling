from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

import pandas as pd


PIPELINE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = next(
    (parent for parent in [PIPELINE_DIR, *PIPELINE_DIR.parents] if (parent / "questionnaire" / "obesity_patient_questionnaire_template.py").exists()),
    PIPELINE_DIR.parent,
)
DEFAULT_RUN_DIR = PIPELINE_DIR / "data" / "obesity_questionnaire_10_persona_comparison_md_background"
QUESTIONNAIRE_TEMPLATE = PROJECT_ROOT / "questionnaire" / "obesity_patient_questionnaire_template.py"

CJK_FONT_STACK = '"Microsoft YaHei", "Microsoft JhengHei", "SimHei", "SimSun", "Noto Sans CJK SC", "PingFang SC", Arial, sans-serif'

META_COLUMNS = {
    "pid",
    "样本编号",
    "variant",
    "variant_folder",
    "variant_label",
    "目标人群细分",
    "BMI配额段",
    "persona_summary",
    "response_style",
    "assumption_notes",
    "consistency_checks",
    "status",
    "error",
}

DEMOGRAPHIC_COLUMNS = [
    "样本编号",
    "个人ID_pid",
    "年龄",
    "性别",
    "年龄配额段",
    "省份",
    "城乡属性",
    "学历",
    "个人就业收入_元_家庭收入近似",
    "收入配额段_近似",
    "BMI",
    "BMI配额段",
    "目标人群细分",
    "合并症类别汇总",
    "全部疾病名称",
    "自评健康",
    "就医行为标签",
    "自付负担分层",
    "运动频率级别",
    "Persona生成线索",
]


def md_cell(text: str) -> dict[str, object]:
    return {"cell_type": "markdown", "metadata": {}, "source": text.splitlines(True)}


def code_cell(text: str) -> dict[str, object]:
    return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": text.splitlines(True)}


def cjk_style_block() -> str:
    return (
        "<style>\n"
        ".jp-Notebook, .jp-RenderedHTMLCommon, .rendered_html, .rendered_html table, "
        ".rendered_html th, .rendered_html td { "
        f"font-family: {CJK_FONT_STACK} !important; "
        "}\n"
        ".rendered_html table { font-size: 13px; }\n"
        ".rendered_html td { vertical-align: top; }\n"
        "</style>\n"
    )


def df_to_markdown(df: pd.DataFrame, max_rows: int | None = None) -> str:
    view = df if max_rows is None else df.head(max_rows)
    if view.empty:
        return "_空表_"
    headers = [str(c).replace("|", "\\|") for c in view.columns]
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for _, row in view.iterrows():
        vals = []
        for col in view.columns:
            text = "" if pd.isna(row[col]) else str(row[col])
            vals.append(text.replace("|", "\\|").replace("\n", "<br>"))
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def load_questionnaire_metadata() -> pd.DataFrame:
    if not QUESTIONNAIRE_TEMPLATE.exists():
        return pd.DataFrame(columns=["题目ID", "问卷部分", "题目文本", "题型", "显示逻辑"])
    spec = importlib.util.spec_from_file_location("obesity_patient_questionnaire_template", QUESTIONNAIRE_TEMPLATE)
    if spec is None or spec.loader is None:
        return pd.DataFrame(columns=["题目ID", "问卷部分", "题目文本", "题型", "显示逻辑"])
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    rows = []
    for item in module.QUESTIONNAIRE:
        if item.qid == "A6":
            derived = [
                ("A6", "A6 尝试次数，按非西医减重措施1-11顺序导出，未经历该措施填0。"),
                ("A6a", "A6a 单次平均坚持时长，按非西医减重措施1-11顺序导出；对应A6为0时填0。"),
                ("A6b", "A6b 月均花费，按非西医减重措施1-11顺序导出；对应A6为0时填0。"),
            ]
        elif item.qid == "A14_A15":
            derived = [
                ("A14", "A14 首诊科室。"),
                ("A15", "A15 接受减重治疗科室。"),
            ]
        elif item.qid == "C4_C5":
            derived = [
                ("C4", "C4 商品名易读性，按商品名1-6顺序导出。"),
                ("C5", "C5 商品名好记程度，按商品名1-6顺序导出。"),
            ]
        else:
            derived = [(item.qid, item.stem)]
        for qid, stem in derived:
            rows.append(
                {
                    "题目ID": qid,
                    "问卷部分": item.section,
                    "题目文本": stem,
                    "题型": item.response_type,
                    "显示逻辑": item.show_if,
                }
            )
    return pd.DataFrame(rows)


def load_section_c_product_card() -> pd.DataFrame:
    if not QUESTIONNAIRE_TEMPLATE.exists():
        return pd.DataFrame()
    spec = importlib.util.spec_from_file_location("obesity_patient_questionnaire_template", QUESTIONNAIRE_TEMPLATE)
    if spec is None or spec.loader is None:
        return pd.DataFrame()
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    rows = []
    for product, attrs in getattr(module, "PRODUCT_CARD", {}).items():
        row = {"产品": product}
        row.update(attrs)
        rows.append(row)
    return pd.DataFrame(rows)


def load_variant(run_dir: Path, folder_name: str, label: str) -> pd.DataFrame:
    path = run_dir / folder_name / "answers.csv"
    if not path.exists():
        raise FileNotFoundError(path)
    df = pd.read_csv(path, dtype=str, keep_default_na=False, encoding="utf-8-sig")
    df["variant_folder"] = folder_name
    df["variant_label"] = label
    return df


def build_comparison_tables(run_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    without_df = load_variant(run_dir, "不含背景信息", "不含背景信息")
    with_df = load_variant(run_dir, "含背景信息", "含背景信息")
    combined = pd.concat([without_df, with_df], ignore_index=True)
    combined.to_csv(run_dir / "comparison_answers_combined.csv", index=False, encoding="utf-8-sig")

    sample = pd.read_csv(run_dir / "selected_10_personas.csv", dtype=str, keep_default_na=False, encoding="utf-8-sig")
    demo_cols = [c for c in DEMOGRAPHIC_COLUMNS if c in sample.columns]
    demographics = sample[demo_cols].copy()
    demographics.to_csv(run_dir / "comparison_selected_persona_demographics.csv", index=False, encoding="utf-8-sig")

    metadata = load_questionnaire_metadata()
    metadata.to_csv(run_dir / "comparison_question_metadata.csv", index=False, encoding="utf-8-sig")
    product_card = load_section_c_product_card()
    if not product_card.empty:
        product_card.to_csv(run_dir / "comparison_section_c_product_card.csv", index=False, encoding="utf-8-sig")

    question_cols = [c for c in without_df.columns if c in with_df.columns and c not in META_COLUMNS]
    merged = without_df.merge(with_df, on="pid", suffixes=("_无背景", "_有背景"))
    sample_key = sample.rename(columns={"个人ID_pid": "pid"})
    merged = merged.merge(sample_key, on="pid", how="left")

    summary_rows = []
    detail_rows = []
    for qid in question_cols:
        left_col = f"{qid}_无背景"
        right_col = f"{qid}_有背景"
        left = merged[left_col].fillna("").astype(str)
        right = merged[right_col].fillna("").astype(str)
        changed = left != right
        pair_counts = (
            pd.DataFrame({"无背景答案": left, "有背景答案": right})
            .groupby(["无背景答案", "有背景答案"])
            .size()
            .reset_index(name="人数")
            .sort_values("人数", ascending=False)
        )
        top_pairs = "；".join(
            f"{row['无背景答案']} -> {row['有背景答案']}（{row['人数']}人）"
            for _, row in pair_counts.head(3).iterrows()
        )
        summary_rows.append(
            {
                "题目ID": qid,
                "比较人数": len(merged),
                "答案变化人数": int(changed.sum()),
                "答案变化率": round(float(changed.mean()), 4) if len(merged) else 0,
                "无背景非空人数": int((left != "").sum()),
                "有背景非空人数": int((right != "").sum()),
                "主要答案迁移": top_pairs,
            }
        )
        for _, row in merged.loc[changed].iterrows():
            detail_rows.append(
                {
                    "题目ID": qid,
                    "pid": row.get("pid", ""),
                    "样本编号": row.get("样本编号", row.get("样本编号_无背景", "")),
                    "年龄": row.get("年龄", ""),
                    "性别": row.get("性别", ""),
                    "省份": row.get("省份", ""),
                    "城乡属性": row.get("城乡属性", ""),
                    "学历": row.get("学历", ""),
                    "BMI": row.get("BMI", ""),
                    "BMI配额段": row.get("BMI配额段", row.get("BMI配额段_无背景", "")),
                    "目标人群细分": row.get("目标人群细分", row.get("目标人群细分_无背景", "")),
                    "合并症类别汇总": row.get("合并症类别汇总", ""),
                    "无背景答案": row.get(left_col, ""),
                    "有背景答案": row.get(right_col, ""),
                    "无背景persona摘要": row.get("persona_summary_无背景", ""),
                    "有背景persona摘要": row.get("persona_summary_有背景", ""),
                }
            )

    differences = pd.DataFrame(summary_rows)
    if not metadata.empty:
        differences = differences.merge(metadata, on="题目ID", how="left")
    differences = differences.sort_values(["答案变化人数", "题目ID"], ascending=[False, True])
    differences.to_csv(run_dir / "comparison_question_differences.csv", index=False, encoding="utf-8-sig")

    detail = pd.DataFrame(detail_rows)
    if not metadata.empty and not detail.empty:
        detail = detail.merge(metadata, on="题目ID", how="left")
    detail = detail.sort_values(["题目ID", "样本编号"]) if not detail.empty else detail
    detail.to_csv(run_dir / "comparison_changed_answer_details.csv", index=False, encoding="utf-8-sig")

    top_qids = differences.head(10)["题目ID"].tolist()
    top_detail = detail[detail["题目ID"].isin(top_qids)].copy() if not detail.empty else detail
    top_detail.to_csv(run_dir / "comparison_top10_changed_answer_details.csv", index=False, encoding="utf-8-sig")

    change_count = detail.groupby("pid").size().reset_index(name="变化题目数") if not detail.empty else pd.DataFrame(columns=["pid", "变化题目数"])
    persona_change = sample.rename(columns={"个人ID_pid": "pid"}).merge(change_count, on="pid", how="left")
    persona_change["变化题目数"] = persona_change["变化题目数"].fillna(0).astype(int)
    keep_cols = [c for c in ["pid", "样本编号", "年龄", "性别", "省份", "城乡属性", "学历", "BMI", "BMI配额段", "目标人群细分", "合并症类别汇总", "变化题目数", "Persona生成线索"] if c in persona_change.columns]
    persona_change = persona_change[keep_cols].sort_values("变化题目数", ascending=False)
    persona_change.to_csv(run_dir / "comparison_persona_change_counts.csv", index=False, encoding="utf-8-sig")

    token_rows = []
    for folder, label in [("不含背景信息", "不含背景信息"), ("含背景信息", "含背景信息")]:
        logs = pd.read_csv(run_dir / folder / "logs.csv", dtype=str, keep_default_na=False, encoding="utf-8-sig")
        for col in ["profile_seconds", "questionnaire_seconds", "profile_total_tokens", "questionnaire_total_tokens", "individual_total_tokens"]:
            logs[col] = pd.to_numeric(logs[col], errors="coerce")
        token_rows.append(
            {
                "版本": label,
                "人数": len(logs),
                "失败人数": int((logs["status"] == "failed").sum()),
                "画像平均秒": round(float(logs["profile_seconds"].mean()), 3),
                "问卷平均秒": round(float(logs["questionnaire_seconds"].mean()), 3),
                "画像总tokens": int(logs["profile_total_tokens"].sum()),
                "问卷总tokens": int(logs["questionnaire_total_tokens"].sum()),
                "总tokens": int(logs["individual_total_tokens"].sum()),
            }
        )
    token_summary = pd.DataFrame(token_rows)
    token_summary.to_csv(run_dir / "comparison_runtime_token_summary.csv", index=False, encoding="utf-8-sig")

    variant_summaries = []
    for folder in ["不含背景信息", "含背景信息"]:
        summary_path = run_dir / folder / "summary.json"
        if summary_path.exists():
            variant_summaries.append(json.loads(summary_path.read_text(encoding="utf-8")))
    output_summary = {
        "source": "rebuilt_from_variant_outputs",
        "run_dir": str(run_dir),
        "selected_sample": str(run_dir / "selected_10_personas.csv"),
        "variants": "both",
        "processed_total": int(sum(item.get("processed", 0) for item in variant_summaries)),
        "failed_total": int(sum(item.get("failed", 0) for item in variant_summaries)),
        "variant_summaries": variant_summaries,
        "comparison_files": {
            "answers_combined": str(run_dir / "comparison_answers_combined.csv"),
            "question_differences": str(run_dir / "comparison_question_differences.csv"),
            "changed_answer_details": str(run_dir / "comparison_changed_answer_details.csv"),
            "notebook": str(run_dir / "with_without_background_comparison_eda.ipynb"),
        },
    }
    (run_dir / "comparison_summary.json").write_text(json.dumps(output_summary, ensure_ascii=False, indent=2), encoding="utf-8")

    return combined, differences, token_summary, demographics, top_detail, persona_change


def build_notebook(
    run_dir: Path,
    combined: pd.DataFrame,
    differences: pd.DataFrame,
    token_summary: pd.DataFrame,
    demographics: pd.DataFrame,
    top_detail: pd.DataFrame,
    persona_change: pd.DataFrame,
) -> dict[str, object]:
    run_dir_text = str(run_dir)
    top_changed = differences.head(20).copy()
    status = combined.groupby(["variant_label", "status"]).size().reset_index(name="人数")
    demographic_summary = demographics[[c for c in ["样本编号", "年龄", "性别", "省份", "城乡属性", "学历", "BMI", "BMI配额段", "目标人群细分", "合并症类别汇总"] if c in demographics.columns]].copy()
    section_c_card_path = run_dir / "comparison_section_c_product_card.csv"
    section_c_card = (
        pd.read_csv(section_c_card_path, dtype=str, keep_default_na=False, encoding="utf-8-sig")
        if section_c_card_path.exists()
        else pd.DataFrame()
    )
    if not persona_change.empty:
        segment_summary = (
            persona_change.groupby([c for c in ["性别", "BMI配额段", "目标人群细分"] if c in persona_change.columns], dropna=False)["变化题目数"]
            .agg(["count", "mean", "max"])
            .reset_index()
            .rename(columns={"count": "人数", "mean": "平均变化题目数", "max": "最高变化题目数"})
        )
        segment_summary["平均变化题目数"] = segment_summary["平均变化题目数"].round(1)
    else:
        segment_summary = pd.DataFrame()

    top_summary_cols = [c for c in ["题目ID", "问卷部分", "题型", "答案变化人数", "答案变化率", "主要答案迁移", "题目文本"] if c in top_changed.columns]
    top_detail_cols = [
        c
        for c in ["题目ID", "问卷部分", "pid", "样本编号", "年龄", "性别", "BMI", "BMI配额段", "目标人群细分", "合并症类别汇总", "无背景答案", "有背景答案", "题目文本"]
        if c in top_detail.columns
    ]
    cells = [
        md_cell(
            cjk_style_block()
            + "# 10人persona问卷作答：有/无背景信息影响分析\n\n"
            "本 notebook 对同一批随机抽取的10位CFPS persona进行比较：一版不提供竞品/产品背景信息，一版提供整理后的 Markdown 背景信息。"
        ),
        md_cell(
            "## 1. 结论导读\n\n"
            "- 本 notebook 不嵌入静态SVG；图表由后续代码单元运行生成。\n"
            "- 重点不再只是运行时间，而是比较背景信息如何改变具体题目答案、哪些persona更容易变化，以及变化集中在哪些问卷模块。\n"
            "- 本版答案导出已按问卷格式拆分A6/A6a/A6b、A14/A15、C4/C5，并用`NA`标记不适用题，适用但未回答保持空白。\n"
            "- `comparison_top10_changed_answer_details.csv` 保存了Top变化题目的逐人答案对照和人口学信息。"
        ),
        md_cell(
            "## 2. 答案导出格式说明\n\n"
            "- `A6`为非西医减重措施1-11的尝试次数序列，`A6a`为对应单次平均坚持时长，`A6b`为对应月均花费；没有经历某项措施的位置填0。\n"
            "- `A14`和`A15`分别代表首诊科室与接受减重治疗科室。\n"
            "- `C4`和`C5`分别代表6个商品名的易读性与好记程度评分序列。\n"
            "- `NA`表示根据show_if逻辑不适用；空白表示该题适用但模型未给出答案或答案无法解析。"
        ),
        md_cell("## 3. C部分产品信息输入示卡\n\n" + df_to_markdown(section_c_card, max_rows=10)),
        md_cell("## 4. 运行状态\n\n" + df_to_markdown(status)),
        md_cell("## 5. 10位persona人口学与健康画像\n\n" + df_to_markdown(demographic_summary, max_rows=10)),
        md_cell("## 6. 每位persona受背景影响的题目数量\n\n" + df_to_markdown(persona_change, max_rows=10)),
        md_cell("## 7. 分人群变化概览\n\n" + df_to_markdown(segment_summary, max_rows=20)),
        md_cell("## 8. 运行耗时与token\n\n" + df_to_markdown(token_summary)),
        md_cell("## 9. Top变化问题总览\n\n" + df_to_markdown(top_changed[top_summary_cols], max_rows=20)),
        md_cell("## 10. Top变化问题逐人答案对照\n\n" + df_to_markdown(top_detail[top_detail_cols], max_rows=80)),
        code_cell(
            "from pathlib import Path\n"
            "import html\n"
            "import pandas as pd\n"
            "from IPython.display import HTML, display\n\n"
            f"RUN_DIR = Path(r'''{run_dir_text}''')\n"
            "pd.set_option('display.unicode.east_asian_width', True)\n"
            "pd.set_option('display.max_colwidth', 160)\n\n"
            "combined = pd.read_csv(RUN_DIR / 'comparison_answers_combined.csv', dtype=str, keep_default_na=False)\n"
            "diff = pd.read_csv(RUN_DIR / 'comparison_question_differences.csv', dtype=str, keep_default_na=False)\n"
            "top_detail = pd.read_csv(RUN_DIR / 'comparison_top10_changed_answer_details.csv', dtype=str, keep_default_na=False)\n"
            "changed_detail = pd.read_csv(RUN_DIR / 'comparison_changed_answer_details.csv', dtype=str, keep_default_na=False)\n"
            "persona_change = pd.read_csv(RUN_DIR / 'comparison_persona_change_counts.csv', dtype=str, keep_default_na=False)\n"
            "demographics = pd.read_csv(RUN_DIR / 'comparison_selected_persona_demographics.csv', dtype=str, keep_default_na=False)\n"
            "token_summary = pd.read_csv(RUN_DIR / 'comparison_runtime_token_summary.csv', dtype=str, keep_default_na=False)\n"
            "combined.shape, diff.shape, top_detail.shape\n"
        ),
        code_cell(
            "CJK_FONT_STACK = 'Microsoft YaHei, Microsoft JhengHei, SimHei, SimSun, Noto Sans CJK SC, PingFang SC, Arial, sans-serif'\n\n"
            "def barh_svg(df, label_col, value_col, title, width=900):\n"
            "    chart = df[[label_col, value_col]].copy()\n"
            "    chart[value_col] = pd.to_numeric(chart[value_col], errors='coerce').fillna(0)\n"
            "    chart = chart.sort_values(value_col, ascending=True)\n"
            "    row_h, left, right, top = 30, 145, 40, 52\n"
            "    height = top + row_h * len(chart) + 32\n"
            "    plot_w = width - left - right\n"
            "    max_value = max(float(chart[value_col].max()), 1.0)\n"
            "    parts = [f'<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"{width}\" height=\"{height}\" viewBox=\"0 0 {width} {height}\">',\n"
            "             f'<rect width=\"{width}\" height=\"{height}\" fill=\"white\"/>',\n"
            "             f'<style>text{{font-family:{CJK_FONT_STACK};fill:#202124}} .title{{font-size:18px;font-weight:700}} .label{{font-size:13px}} .value{{font-size:12px;fill:#4b5563}}</style>',\n"
            "             f'<text class=\"title\" x=\"{left}\" y=\"28\">{html.escape(title)}</text>']\n"
            "    for i, row in enumerate(chart.to_dict('records')):\n"
            "        y = top + i * row_h\n"
            "        value = float(row[value_col])\n"
            "        bar_w = max(2, value / max_value * plot_w)\n"
            "        label = html.escape(str(row[label_col]))\n"
            "        parts += [f'<text class=\"label\" x=\"{left-10}\" y=\"{y+16}\" text-anchor=\"end\">{label}</text>',\n"
            "                  f'<rect x=\"{left}\" y=\"{y}\" width=\"{bar_w:.1f}\" height=\"18\" rx=\"3\" fill=\"#2563eb\"/>',\n"
            "                  f'<text class=\"value\" x=\"{left+bar_w+6:.1f}\" y=\"{y+14}\">{value:g}</text>']\n"
            "    parts.append('</svg>')\n"
            "    return '\\n'.join(parts)\n\n"
            "display(HTML(barh_svg(diff.head(20), '题目ID', '答案变化人数', 'Top20题目：答案变化人数')))\n"
        ),
        code_cell(
            "display(HTML(barh_svg(persona_change.sort_values('变化题目数', ascending=False), '样本编号', '变化题目数', '每位persona受背景影响的题目数量')))\n"
        ),
        code_cell(
            "top_questions = diff.head(10)['题目ID'].tolist()\n"
            "top_detail[top_detail['题目ID'].isin(top_questions)][['题目ID','问卷部分','题目文本','样本编号','年龄','性别','BMI','BMI配额段','目标人群细分','无背景答案','有背景答案']]\n"
        ),
        code_cell(
            "pair_summary = (top_detail.groupby(['题目ID','问卷部分','无背景答案','有背景答案'])\n"
            "                .size().reset_index(name='人数')\n"
            "                .sort_values(['题目ID','人数'], ascending=[True, False]))\n"
            "pair_summary.head(80)\n"
        ),
        code_cell(
            "section_c_questions = ['C1','C2','C3','C4','C5','C6','C7']\n"
            "section_c_diff = diff[diff['题目ID'].isin(section_c_questions)]\n"
            "section_c_pairs = (changed_detail[changed_detail['题目ID'].isin(section_c_questions)]\n"
            "                   .groupby(['题目ID','问卷部分','无背景答案','有背景答案'])\n"
            "                   .size().reset_index(name='人数')\n"
            "                   .sort_values(['题目ID','人数'], ascending=[True, False]))\n"
            "display(section_c_diff[['题目ID','问卷部分','答案变化人数','答案变化率','主要答案迁移','题目文本']])\n"
            "display(section_c_pairs.head(80))\n"
        ),
        code_cell(
            "section_c_personas = changed_detail[changed_detail['题目ID'].isin(['C1','C2','C3','C4','C5','C6','C7'])]\n"
            "section_c_personas[['题目ID','样本编号','年龄','性别','BMI','BMI配额段','目标人群细分','合并症类别汇总','无背景答案','有背景答案','题目文本']].head(120)\n"
        ),
        code_cell(
            "persona_profile_cols = ['variant_label','pid','样本编号','目标人群细分','BMI配额段','persona_summary','response_style','assumption_notes']\n"
            "combined[[c for c in persona_profile_cols if c in combined.columns]].sort_values(['pid','variant_label'])\n"
        ),
    ]
    return {
        "cells": cells,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3.x"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build EDA notebook comparing with/without background questionnaire outputs.")
    parser.add_argument("--run-dir", default=str(DEFAULT_RUN_DIR))
    args = parser.parse_args()
    run_dir = Path(args.run_dir)
    combined, differences, token_summary, demographics, top_detail, persona_change = build_comparison_tables(run_dir)
    notebook = build_notebook(run_dir, combined, differences, token_summary, demographics, top_detail, persona_change)
    notebook_path = run_dir / "with_without_background_comparison_eda.ipynb"
    notebook_path.write_text(json.dumps(notebook, ensure_ascii=False, indent=2), encoding="utf-8")
    print(notebook_path)


if __name__ == "__main__":
    main()
