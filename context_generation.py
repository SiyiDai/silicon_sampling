import csv


def load_survey_rows(csv_file):
    """
    Load a Qualtrics-style CSV and yield rows as dicts.

    The file includes multiple header/metadata rows. Row 2 contains the field names.
    """
    with open(csv_file, newline="", encoding="utf-8") as handle:
        reader = csv.reader(handle)
        _ = next(reader)  # Column1..ColumnN
        fieldnames = next(reader)
        labels = next(reader)  # human-readable labels
        _ = next(reader)  # import metadata
        for row in reader:
            if not row or all(not cell.strip() for cell in row):
                continue
            yield fieldnames, labels, dict(zip(fieldnames, row))


def build_prediction_context(row, labels):
    """
    Build a structured context from all question/answer pairs except Q48.
    """
    label_map = dict(zip(row.keys(), labels))
    qa_lines = []
    for key, answer in row.items():
        if not key.startswith("Q"):
            continue
        if key == "Q48":
            continue
        if not answer:
            continue
        question = label_map.get(key) or key
        question = question.replace("\n", " ").strip()
        qa_lines.append(f"{question} Answer: {answer}")

    if not qa_lines:
        return "No survey responses available."

    return "\n".join(qa_lines)
