# Obesity Patient Pipeline 210

This folder is the full-sample version of `obesity_patient_pipeline`. It keeps the 10-person trial folder intact and is configured for all 210 cleaned CFPS obesity-patient personas.

## What Is Included

- `data/清洗后_210样本.csv`: the full cleaned 210-person input dataset.
- `questionnaire_generation.py`: generates persona first, then answers the obesity questionnaire as that persona.
- `data_generation.py`: shared prompt/client logic, using `real_individual_pipeline/get_api_key.py`.
- `context_generation.py`: converts each CFPS row into grounded Chinese seed context.
- `build_comparison_eda_notebook.py`: rebuilds comparison tables and the EDA notebook after a run.
- `data_processing.py` and `prototype.py`: wrapper entry points.

## Background Prompt

The with-background version no longer passes the mixed English/Chinese Markdown bullets directly to personas. Instead, `questionnaire_generation.py` converts the source file into a stable Chinese lecture-style pre-reading that explains GLP-1, GIP,胰高糖素双靶点, MASH/metabolic-health relevance, and major drug/brand positioning in connected prose.

The background is treated as shared pre-survey information. It may influence how a persona understands mechanisms, product cards and brand context, but it must not rewrite CFPS hard facts or make every persona prefer the same product.

## Run Full 210 Personas

This will make two runs, one without background and one with background. For 210 people, that means 420 persona/questionnaire workflows, so run it only when ready for the API cost and time.

```powershell
python questionnaire_generation.py --variants both
```

Outputs are written to:

`data/obesity_questionnaire_210_persona_full_comparison/`

The script also writes `selected_personas.csv` and `selected_210_personas.csv` so the EDA builder can find the full sample consistently.

## Build EDA Notebook

After the full run completes:

```powershell
python build_comparison_eda_notebook.py
```

The notebook will be written to:

`data/obesity_questionnaire_210_persona_full_comparison/with_without_background_comparison_eda.ipynb`

## Answer Export Format

The CSV export follows questionnaire order. `A6`, `A6a`, and `A6b` are aligned 1-11 method-code series for attempts, average duration and monthly cost. `A14`/`A15` and `C4`/`C5` are separate columns. Not-applicable fields are marked `NA`; applicable but unanswered fields remain blank.
