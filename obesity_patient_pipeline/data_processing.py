from __future__ import annotations

from questionnaire_generation import process_questionnaire_comparison


def process_obesity_questionnaire_comparison(
    input_file: str,
    output_dir: str,
    limit: int = 10,
    seed: int = 20260528,
) -> dict[str, object]:
    return process_questionnaire_comparison(
        input_file=input_file,
        output_dir=output_dir,
        limit=limit,
        seed=seed,
        variants="both",
    )

