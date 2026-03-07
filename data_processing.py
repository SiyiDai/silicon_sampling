import csv
import re

from context_generation import build_prediction_context, load_survey_rows
from data_generation import generate_star_rating


def _normalize_star(value):
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return int(value)
    match = re.search(r"[1-5]", str(value))
    return int(match.group(0)) if match else None


def compute_metrics_from_output(output_csv):
    """
    Compute accuracy metrics directly from the saved predictions CSV.

    Returns a dict with: total, exact_match, within_1, mae.
    """
    total = 0
    correct = 0
    within_1 = 0
    abs_error = 0

    with open(output_csv, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            predicted = _normalize_star(row.get("Predicted_Q48"))
            actual = _normalize_star(row.get("Actual_Q48"))
            if actual is None or predicted is None:
                continue
            total += 1
            if predicted == actual:
                correct += 1
            if abs(predicted - actual) <= 1:
                within_1 += 1
            abs_error += abs(predicted - actual)

    exact_match = (correct / total) if total else 0.0
    within_1_acc = (within_1 / total) if total else 0.0
    mae = (abs_error / total) if total else 0.0

    return {
        "total": total,
        "correct": correct,
        "within_1_count": within_1,
        "exact_match": exact_match,
        "within_1": within_1_acc,
        "mae": mae,
    }


def process_predictions(input_csv, output_csv, limit=None):
    """
    Predict Q48 (star rating) from all other questions and report accuracy.

    Args:
        input_csv (str): Path to the input CSV file with survey responses.
        output_csv (str): Path to the output CSV file to save predictions.
        limit (int | None): Optional max number of rows to process.
    """
    output_fields = ["ResponseId", "Predicted_Q48", "Actual_Q48", "LLM_Raw"]
    processed = 0

    with open(output_csv, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=output_fields)
        writer.writeheader()

        for _, labels, row in load_survey_rows(input_csv):
            context = build_prediction_context(row, labels)
            result = generate_star_rating(context)

            predicted = _normalize_star(result["star_rating"])
            actual = _normalize_star(row.get("Q48"))

            writer.writerow(
                {
                    "ResponseId": row.get("ResponseId"),
                    "Predicted_Q48": predicted,
                    "Actual_Q48": actual,
                    "LLM_Raw": result["raw"],
                }
            )

            processed += 1
            if limit is not None and processed >= limit:
                break

    metrics = compute_metrics_from_output(output_csv)
    print(
        f"Processed {processed} rows. "
        f"Exact match: {metrics['exact_match']:.3f} "
        f"({metrics['correct']}/{metrics['total']}), "
        f"Within-1: {metrics['within_1']:.3f} "
        f"({metrics['within_1_count']}/{metrics['total']}), "
        f"MAE: {metrics['mae']:.3f}. "
        f"Output saved to {output_csv}"
    )
