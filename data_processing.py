from __future__ import annotations

import csv
import json
import re
from typing import Dict, Iterable, List, Sequence

from context_generation import (
    PERSONA_SOURCE_KEYS,
    build_label_map,
    build_persona_seed_context,
    build_target_question_map,
    read_survey_table,
)
from data_generation import answer_questions_as_persona, generate_persona


_WHITESPACE_RE = re.compile(r"\s+")


def _normalize_text(value) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    return _WHITESPACE_RE.sub(" ", text).casefold()


def compute_exact_match_metrics_from_output(
    output_csv: str,
    target_question_keys: Sequence[str],
) -> Dict[str, object]:
    """
    Compute simple exact-match metrics from the saved predictions CSV.
    """
    total = 0
    correct = 0
    per_question: Dict[str, Dict[str, int]] = {
        key: {"total": 0, "correct": 0} for key in target_question_keys
    }

    with open(output_csv, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            for key in target_question_keys:
                predicted = _normalize_text(row.get(f"Predicted_{key}"))
                actual = _normalize_text(row.get(f"Actual_{key}"))
                if predicted is None or actual is None:
                    continue

                total += 1
                per_question[key]["total"] += 1
                if predicted == actual:
                    correct += 1
                    per_question[key]["correct"] += 1

    overall_exact_match = (correct / total) if total else 0.0
    for key, stats in per_question.items():
        q_total = stats["total"]
        stats["exact_match"] = (stats["correct"] / q_total) if q_total else 0.0

    return {
        "total_answers_compared": total,
        "correct_answers": correct,
        "overall_exact_match": overall_exact_match,
        "per_question": per_question,
    }


def process_persona_predictions(input_file: str, output_csv: str, limit: int | None = None) -> Dict[str, object]:
    """
    Create personas from the specified seed questions and ask those personas to answer all remaining questions.

    Args:
        input_file: Path to Qualtrics-style CSV or XLSX data.
        output_csv: Output CSV path.
        limit: Optional maximum number of rows to process.
    """
    fieldnames, labels, rows = read_survey_table(input_file)
    if not rows:
        raise ValueError("No survey rows found in input file.")

    label_map = build_label_map(fieldnames, labels)
    target_questions = build_target_question_map(
        fieldnames,
        label_map,
        excluded_keys=PERSONA_SOURCE_KEYS,
    )
    target_question_keys = list(target_questions.keys())

    output_fields = [
        "PersonaId",
        "SourceIndex",
        "PersonaSeedColumns",
        "PersonaSeedContext",
        "PersonaSummary",
        "PersonaVoice",
        "PersonaTraits",
    ]
    output_fields.extend(f"Predicted_{key}" for key in target_question_keys)
    output_fields.extend(f"Actual_{key}" for key in target_question_keys)
    output_fields.extend(["PersonaRaw", "AnswersRaw"])

    processed = 0

    with open(output_csv, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=output_fields)
        writer.writeheader()

        for index, row in enumerate(rows, start=1):
            if limit is not None and processed >= limit:
                break

            persona_id = str(row.get("ResponseId") or index)
            persona_seed_context = build_persona_seed_context(
                row,
                label_map,
                persona_keys=PERSONA_SOURCE_KEYS,
            )

            persona = generate_persona(persona_id=persona_id, persona_seed_context=persona_seed_context)
            answer_bundle = answer_questions_as_persona(
                persona_id=persona_id,
                persona=persona,
                persona_seed_context=persona_seed_context,
                target_questions=target_questions,
            )
            predicted_answers = answer_bundle.get("answers", {})
            if not isinstance(predicted_answers, dict):
                predicted_answers = {}

            output_row = {
                "PersonaId": persona_id,
                "SourceIndex": index,
                "PersonaSeedColumns": ",".join(PERSONA_SOURCE_KEYS),
                "PersonaSeedContext": persona_seed_context,
                "PersonaSummary": persona.get("persona_summary", ""),
                "PersonaVoice": persona.get("voice", ""),
                "PersonaTraits": json.dumps(persona.get("traits", []), ensure_ascii=False),
                "PersonaRaw": persona.get("raw", ""),
                "AnswersRaw": answer_bundle.get("raw", ""),
            }

            for key in target_question_keys:
                output_row[f"Predicted_{key}"] = predicted_answers.get(key, "")
                output_row[f"Actual_{key}"] = row.get(key, "")

            writer.writerow(output_row)
            processed += 1

    metrics = compute_exact_match_metrics_from_output(output_csv, target_question_keys)
    print(
        f"Processed {processed} personas across {len(target_question_keys)} target questions. "
        f"Overall exact match: {metrics['overall_exact_match']:.3f} "
        f"({metrics['correct_answers']}/{metrics['total_answers_compared']}). "
        f"Output saved to {output_csv}"
    )
    return metrics
