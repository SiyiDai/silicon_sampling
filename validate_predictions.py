from __future__ import annotations

import argparse
import csv
import json
import math
import re
from collections import Counter
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Sequence, Tuple

from context_generation import PERSONA_SOURCE_KEYS, read_survey_table


DEFAULT_GROUP_COLUMNS = ["Q29", "Q30", "Q31"]
LIKERT_TEXT_MAP = [
    ("strongly disagree", 1.0),
    ("somewhat disagree", 3.0),
    ("slightly disagree", 3.0),
    ("disagree", 2.0),
    ("neither agree nor disagree", 4.0),
    ("neutral", 4.0),
    ("somewhat agree", 5.0),
    ("slightly agree", 5.0),
    ("strongly agree", 7.0),
    ("agree", 6.0),
]


def _clean_text(value) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    if not text or text.casefold() in {"nan", "none", "null"}:
        return ""
    return re.sub(r"\s+", " ", text)


def _canonical_label(value) -> str | None:
    text = _clean_text(value)
    if not text:
        return None
    number = _to_number(text)
    if number is not None:
        rounded = round(number)
        if abs(number - rounded) < 1e-9:
            return str(int(rounded))
        return f"{number:.6g}"
    return text.casefold()


def _to_number(value) -> float | None:
    text = _clean_text(value)
    if not text:
        return None

    numeric_match = re.search(r"(?<!\d)-?\d+(?:\.\d+)?", text.replace(",", ""))
    if numeric_match:
        try:
            return float(numeric_match.group(0))
        except ValueError:
            pass

    lowered = text.casefold()
    for phrase, score in LIKERT_TEXT_MAP:
        if phrase in lowered:
            return score
    return None


def _safe_divide(numerator: float, denominator: float) -> float | None:
    if denominator == 0:
        return None
    return numerator / denominator


def _mean(values: Sequence[float]) -> float | None:
    return _safe_divide(sum(values), len(values))


def _rmse(actual: Sequence[float], predicted: Sequence[float]) -> float | None:
    if not actual:
        return None
    return math.sqrt(sum((a - p) ** 2 for a, p in zip(actual, predicted)) / len(actual))

def _euclidean(actual: Sequence[float], predicted: Sequence[float]) -> float | None:
    if not actual or len(actual) != len(predicted):
        return None
    return math.sqrt(sum((a - p) ** 2 for a, p in zip(actual, predicted)))


def _pearson(x: Sequence[float], y: Sequence[float]) -> float | None:
    if len(x) < 2 or len(y) < 2 or len(x) != len(y):
        return None
    mean_x = _mean(x)
    mean_y = _mean(y)
    if mean_x is None or mean_y is None:
        return None
    x_centered = [value - mean_x for value in x]
    y_centered = [value - mean_y for value in y]
    denom_x = math.sqrt(sum(value * value for value in x_centered))
    denom_y = math.sqrt(sum(value * value for value in y_centered))
    if denom_x == 0 or denom_y == 0:
        return None
    numerator = sum(a * b for a, b in zip(x_centered, y_centered))
    return numerator / (denom_x * denom_y)


def _rankdata(values: Sequence[float]) -> List[float]:
    indexed = sorted(enumerate(values), key=lambda item: item[1])
    ranks = [0.0] * len(values)
    index = 0
    while index < len(indexed):
        end = index
        while end + 1 < len(indexed) and indexed[end + 1][1] == indexed[index][1]:
            end += 1
        average_rank = (index + end + 2) / 2.0
        for offset in range(index, end + 1):
            original_position = indexed[offset][0]
            ranks[original_position] = average_rank
        index = end + 1
    return ranks


def _spearman(x: Sequence[float], y: Sequence[float]) -> float | None:
    if len(x) < 2 or len(y) < 2 or len(x) != len(y):
        return None
    return _pearson(_rankdata(x), _rankdata(y))


def _distribution_metrics(actual_labels: Sequence[str], predicted_labels: Sequence[str]) -> Dict[str, float | None]:
    if not actual_labels:
        return {"tvd": None, "js_divergence": None}

    actual_counts = Counter(actual_labels)
    predicted_counts = Counter(predicted_labels)
    labels = sorted(set(actual_counts) | set(predicted_counts))
    total_actual = sum(actual_counts.values())
    total_predicted = sum(predicted_counts.values())
    if total_actual == 0 or total_predicted == 0:
        return {"tvd": None, "js_divergence": None}

    tvd = 0.0
    js_divergence = 0.0
    for label in labels:
        p = actual_counts[label] / total_actual
        q = predicted_counts[label] / total_predicted
        m = 0.5 * (p + q)
        tvd += abs(p - q)
        if p > 0 and m > 0:
            js_divergence += 0.5 * p * math.log(p / m, 2)
        if q > 0 and m > 0:
            js_divergence += 0.5 * q * math.log(q / m, 2)

    return {"tvd": 0.5 * tvd, "js_divergence": js_divergence}


def _classification_metrics(actual_labels: Sequence[str], predicted_labels: Sequence[str]) -> Dict[str, float | int | None]:
    total = len(actual_labels)
    if total == 0:
        return {
            "compared": 0,
            "exact_match": None,
            "macro_precision": None,
            "macro_recall": None,
            "macro_f1": None,
            "weighted_f1": None,
        }

    correct = sum(1 for actual, predicted in zip(actual_labels, predicted_labels) if actual == predicted)
    label_set = sorted(set(actual_labels) | set(predicted_labels))

    macro_precision_values: List[float] = []
    macro_recall_values: List[float] = []
    macro_f1_values: List[float] = []
    weighted_f1_sum = 0.0

    for label in label_set:
        tp = sum(1 for actual, predicted in zip(actual_labels, predicted_labels) if actual == label and predicted == label)
        fp = sum(1 for actual, predicted in zip(actual_labels, predicted_labels) if actual != label and predicted == label)
        fn = sum(1 for actual, predicted in zip(actual_labels, predicted_labels) if actual == label and predicted != label)
        support = sum(1 for actual in actual_labels if actual == label)

        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        f1 = (2 * precision * recall / (precision + recall)) if precision + recall else 0.0

        macro_precision_values.append(precision)
        macro_recall_values.append(recall)
        macro_f1_values.append(f1)
        weighted_f1_sum += support * f1

    return {
        "compared": total,
        "exact_match": correct / total,
        "macro_precision": sum(macro_precision_values) / len(macro_precision_values),
        "macro_recall": sum(macro_recall_values) / len(macro_recall_values),
        "macro_f1": sum(macro_f1_values) / len(macro_f1_values),
        "weighted_f1": weighted_f1_sum / total,
    }


def _numeric_metrics(actual_values: Sequence[float], predicted_values: Sequence[float]) -> Dict[str, float | int | None]:
    if not actual_values:
        return {
            "numeric_compared": 0,
            "euclidean_distance": None,
            "mean_actual": None,
            "mean_predicted": None,
            "mean_bias": None,
            "pearson": None,
            "spearman": None,
        }

    signed_errors = [predicted - actual for actual, predicted in zip(actual_values, predicted_values)]
    return {
        "numeric_compared": len(actual_values),
        "euclidean_distance": _euclidean(actual_values, predicted_values),
        "mean_actual": _mean(actual_values),
        "mean_predicted": _mean(predicted_values),
        "mean_bias": _mean(signed_errors),
        "pearson": _pearson(actual_values, predicted_values),
        "spearman": _spearman(actual_values, predicted_values),
    }

def _compute_metrics(pairs: Sequence[Tuple[object, object]]) -> Dict[str, float | int | None]:
    cleaned_pairs = [(_clean_text(actual), _clean_text(predicted)) for actual, predicted in pairs]
    cleaned_pairs = [(actual, predicted) for actual, predicted in cleaned_pairs if actual and predicted]

    actual_labels: List[str] = []
    predicted_labels: List[str] = []
    actual_numbers: List[float] = []
    predicted_numbers: List[float] = []

    for actual, predicted in cleaned_pairs:
        actual_label = _canonical_label(actual)
        predicted_label = _canonical_label(predicted)
        if actual_label is None or predicted_label is None:
            continue
        actual_labels.append(actual_label)
        predicted_labels.append(predicted_label)

        actual_number = _to_number(actual)
        predicted_number = _to_number(predicted)
        if actual_number is not None and predicted_number is not None:
            actual_numbers.append(actual_number)
            predicted_numbers.append(predicted_number)

    metrics = {}
    metrics.update(_classification_metrics(actual_labels, predicted_labels))
    metrics.update(_numeric_metrics(actual_numbers, predicted_numbers))
    metrics.update(_distribution_metrics(actual_labels, predicted_labels))
    return metrics


def _read_predictions_csv(csv_file: str) -> List[Dict[str, str]]:
    with open(csv_file, newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _infer_question_keys(rows: Sequence[Mapping[str, object]]) -> List[str]:
    if not rows:
        return []
    columns = rows[0].keys()
    keys: List[str] = []
    for column in columns:
        if not column.startswith("Predicted_"):
            continue
        question_key = column[len("Predicted_"):]
        if f"Actual_{question_key}" in columns:
            keys.append(question_key)
    return keys


def _build_source_lookup(table_file: str) -> Dict[str, Dict[str, str]]:
    fieldnames, _, rows = read_survey_table(table_file)
    lookup: Dict[str, Dict[str, str]] = {}
    for index, row in enumerate(rows, start=1):
        source_index = str(index)
        persona_id = str(row.get("ResponseId") or index)
        enriched_row = {key: _clean_text(value) for key, value in row.items() if key in fieldnames}
        enriched_row["SourceIndex"] = source_index
        enriched_row["PersonaId"] = persona_id
        lookup[source_index] = enriched_row
        lookup[f"persona:{persona_id}"] = enriched_row
    return lookup


def _enrich_rows_with_source_data(
    prediction_rows: List[Dict[str, str]],
    source_lookup: Mapping[str, Mapping[str, str]],
    group_columns: Sequence[str],
) -> None:
    for row in prediction_rows:
        source_index = _clean_text(row.get("SourceIndex"))
        persona_id = _clean_text(row.get("PersonaId"))
        source_row = source_lookup.get(source_index) or source_lookup.get(f"persona:{persona_id}")
        if not source_row:
            continue
        for column in group_columns:
            if not _clean_text(row.get(column)):
                row[column] = _clean_text(source_row.get(column))
        for column in PERSONA_SOURCE_KEYS:
            seed_column = f"Seed_{column}"
            if seed_column not in row or not _clean_text(row.get(seed_column)):
                row[seed_column] = _clean_text(source_row.get(column))


def _write_csv(path: str | Path, rows: Sequence[Mapping[str, object]], field_order: Sequence[str] | None = None) -> None:
    path = str(path)
    if field_order is None:
        seen: List[str] = []
        for row in rows:
            for key in row.keys():
                if key not in seen:
                    seen.append(key)
        field_order = seen
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(field_order))
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def _serialize_metric_row(base: Mapping[str, object], metrics: Mapping[str, object]) -> Dict[str, object]:
    row = dict(base)
    for key, value in metrics.items():
        row[key] = value
    return row


def validate_predictions(
    predictions_csv: str,
    source_input: str | None,
    output_dir: str,
    group_columns: Sequence[str] | None = None,
) -> Dict[str, object]:
    group_columns = list(group_columns or DEFAULT_GROUP_COLUMNS)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    prediction_rows = _read_predictions_csv(predictions_csv)
    if not prediction_rows:
        raise ValueError("No prediction rows found in the predictions CSV.")

    question_keys = _infer_question_keys(prediction_rows)
    if not question_keys:
        raise ValueError("Could not find any Predicted_/Actual_ question pairs in the predictions CSV.")

    if source_input:
        source_lookup = _build_source_lookup(source_input)
        _enrich_rows_with_source_data(prediction_rows, source_lookup, group_columns)

    persona_rows: List[Dict[str, object]] = []
    for row in prediction_rows:
        row_pairs = [
            (row.get(f"Actual_{question_key}"), row.get(f"Predicted_{question_key}"))
            for question_key in question_keys
        ]
        metrics = _compute_metrics(row_pairs)
        persona_row = {
            "PersonaId": _clean_text(row.get("PersonaId")) or _clean_text(row.get("SourceIndex")),
            "SourceIndex": _clean_text(row.get("SourceIndex")),
        }
        for group_col in group_columns:
            persona_row[group_col] = _clean_text(row.get(group_col))
        persona_rows.append(_serialize_metric_row(persona_row, metrics))

    question_metric_rows: List[Dict[str, object]] = []
    overall_pairs: List[Tuple[object, object]] = []
    for question_key in question_keys:
        pairs = [
            (row.get(f"Actual_{question_key}"), row.get(f"Predicted_{question_key}"))
            for row in prediction_rows
        ]
        overall_pairs.extend(pairs)
        metrics = _compute_metrics(pairs)
        question_metric_rows.append(_serialize_metric_row({"question": question_key}, metrics))

    overall_metrics = _compute_metrics(overall_pairs)

    group_rows: List[Dict[str, object]] = []
    group_question_rows: List[Dict[str, object]] = []
    trend_rows: List[Dict[str, object]] = []
    trend_detail_rows: List[Dict[str, object]] = []

    for group_col in group_columns:
        values = sorted({_clean_text(row.get(group_col)) for row in prediction_rows if _clean_text(row.get(group_col))})
        for group_value in values:
            group_subset = [row for row in prediction_rows if _clean_text(row.get(group_col)) == group_value]
            group_pairs: List[Tuple[object, object]] = []
            for question_key in question_keys:
                question_pairs = [
                    (row.get(f"Actual_{question_key}"), row.get(f"Predicted_{question_key}"))
                    for row in group_subset
                ]
                group_pairs.extend(question_pairs)
                metrics = _compute_metrics(question_pairs)
                group_question_rows.append(
                    _serialize_metric_row(
                        {
                            "group_column": group_col,
                            "group_value": group_value,
                            "question": question_key,
                        },
                        metrics,
                    )
                )

                actual_numbers = [
                    _to_number(row.get(f"Actual_{question_key}"))
                    for row in group_subset
                    if _to_number(row.get(f"Actual_{question_key}")) is not None
                ]
                predicted_numbers = [
                    _to_number(row.get(f"Predicted_{question_key}"))
                    for row in group_subset
                    if _to_number(row.get(f"Predicted_{question_key}")) is not None
                ]
                if actual_numbers and predicted_numbers:
                    trend_detail_rows.append(
                        {
                            "group_column": group_col,
                            "group_value": group_value,
                            "question": question_key,
                            "group_size": len(group_subset),
                            "actual_mean": _mean(actual_numbers),
                            "predicted_mean": _mean(predicted_numbers),
                            "mean_gap": (_mean(predicted_numbers) or 0) - (_mean(actual_numbers) or 0),
                        }
                    )

            metrics = _compute_metrics(group_pairs)
            group_rows.append(
                _serialize_metric_row(
                    {
                        "group_column": group_col,
                        "group_value": group_value,
                        "group_size": len(group_subset),
                    },
                    metrics,
                )
            )

        for question_key in question_keys:
            detail_subset = [
                row for row in trend_detail_rows
                if row["group_column"] == group_col and row["question"] == question_key
            ]
            if len(detail_subset) < 2:
                continue
            actual_means = [float(row["actual_mean"]) for row in detail_subset if row.get("actual_mean") is not None]
            predicted_means = [float(row["predicted_mean"]) for row in detail_subset if row.get("predicted_mean") is not None]
            if len(actual_means) != len(predicted_means) or len(actual_means) < 2:
                continue
            trend_rows.append(
                {
                    "group_column": group_col,
                    "question": question_key,
                    "num_groups": len(detail_subset),
                    "euclidean_distance_across_group_means": _euclidean(actual_means, predicted_means),
                    "pearson_group_mean_correlation": _pearson(actual_means, predicted_means),
                    "spearman_group_mean_correlation": _spearman(actual_means, predicted_means),
                }
            )

    summary = {
        "predictions_csv": str(predictions_csv),
        "source_input": str(source_input) if source_input else None,
        "output_dir": str(output_path),
        "num_personas": len(prediction_rows),
        "num_questions": len(question_keys),
        "question_keys": question_keys,
        "group_columns": list(group_columns),
        "overall": overall_metrics,
        "artifacts": {
            "persona_metrics_csv": str(output_path / "persona_metrics.csv"),
            "question_metrics_csv": str(output_path / "question_metrics.csv"),
            "group_metrics_csv": str(output_path / "group_metrics.csv"),
            "group_question_metrics_csv": str(output_path / "group_question_metrics.csv"),
            "trend_metrics_csv": str(output_path / "trend_metrics.csv"),
            "trend_detail_csv": str(output_path / "trend_detail.csv"),
            "summary_json": str(output_path / "validation_summary.json"),
        },
    }

    _write_csv(output_path / "persona_metrics.csv", persona_rows)
    _write_csv(output_path / "question_metrics.csv", question_metric_rows)
    _write_csv(output_path / "group_metrics.csv", group_rows)
    _write_csv(output_path / "group_question_metrics.csv", group_question_rows)
    _write_csv(output_path / "trend_metrics.csv", trend_rows)
    _write_csv(output_path / "trend_detail.csv", trend_detail_rows)
    with open(output_path / "validation_summary.json", "w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, ensure_ascii=False)

    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=(
            "Validate persona-based survey predictions with persona-wise, question-wise, "
            "group-wise, and trend-level metrics."
        )
    )
    parser.add_argument("--predictions", required=True, help="CSV created by the persona prediction pipeline")
    parser.add_argument(
        "--source-input",
        default=None,
        help="Original survey CSV/XLSX used to generate predictions. Needed for demographic group validation if not already present in the predictions CSV.",
    )
    parser.add_argument(
        "--output-dir",
        default="/mnt/data/validation_report",
        help="Directory where validation outputs will be written",
    )
    parser.add_argument(
        "--group-cols",
        nargs="*",
        default=DEFAULT_GROUP_COLUMNS,
        help="Columns to use for grouped validation, e.g. Q29 Q30 Q31",
    )
    args = parser.parse_args()

    summary = validate_predictions(
        predictions_csv=args.predictions,
        source_input=args.source_input,
        output_dir=args.output_dir,
        group_columns=args.group_cols,
    )

    overall = summary.get("overall", {})
    exact_match = overall.get("exact_match")
    macro_f1 = overall.get("macro_f1")
    spearman = overall.get("spearman")
    euclidean = overall.get("euclidean_distance")
    compared = overall.get("compared")
    message_parts = ["Validation complete.", f"Compared answers: {compared}"]
    if isinstance(exact_match, float):
        message_parts.append(f"Exact match: {exact_match:.3f}")
    if isinstance(macro_f1, float):
        message_parts.append(f"Macro-F1: {macro_f1:.3f}")
    if isinstance(spearman, float):
        message_parts.append(f"Spearman: {spearman:.3f}")
    if isinstance(euclidean, float):
        message_parts.append(f"Euclidean distance: {euclidean:.3f}")
    print("; ".join(message_parts))
    print(f"Summary written to {summary['artifacts']['summary_json']}")









