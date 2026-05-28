# Obesity Patient Pipeline

This pipeline mirrors `real_individual_pipeline`, but targets the strict 210-person Chinese CFPS obesity-patient sample and the full obesity patient questionnaire.

## Files

- `context_generation.py`: reads the cleaned 210-person CSV and builds grounded Chinese seed context.
- `data_generation.py`: creates a vivid persona first, then exposes prompt/client utilities for questionnaire answering.
- `questionnaire_generation.py`: randomly samples personas, runs with-background and without-background questionnaire simulations, and writes answers/logs.
- `data_processing.py`: small programmatic wrapper.
- `prototype.py`: command-line alias for `questionnaire_generation.py`.
- `build_comparison_eda_notebook.py`: builds the EDA notebook comparing both prompt variants.
- `脚本逻辑分析.md`: notes from reading the earlier scripts.
- `../questionnaire/obesity_patient_questionnaire_template.py`: self-contained questionnaire template used by this branch, including the C-section product information card transcribed from the image table.

## Default Inputs

- Strict sample: `data/persona_seed/肥胖患者210样本_清洗与EDA_中文/清洗后_210样本.csv`
- Questionnaire template: `questionnaire/obesity_patient_questionnaire_template.py`
- Background document: `C:\Users\siyid\Downloads\Survo competitor.md`
- API key: reused from `real_individual_pipeline/get_api_key.py`

## Run 10 Personas, Both Variants

```powershell
python questionnaire_generation.py --limit 10 --variants both
```

The script writes:

- `data/obesity_questionnaire_10_persona_comparison/selected_10_personas.csv`
- `data/obesity_questionnaire_10_persona_comparison/不含背景信息/answers.csv`
- `data/obesity_questionnaire_10_persona_comparison/含背景信息/answers.csv`
- `logs.csv`, `personas_and_answers.jsonl`, prompt templates, background text and summary JSON for each variant.

The Markdown background is cleaned and organized before being injected into prompts. The script preserves the full Markdown-derived content by default and adds explicit rules so personas use it as market/competitor context, not as personal medical history.

The answer CSV is exported in questionnaire order. `A6`, `A6a`, and `A6b` are split into aligned 1-11 method-code series for attempts, average duration, and monthly cost. `A14`/`A15` and `C4`/`C5` are also split into separate columns. Not-applicable fields are marked `NA`; applicable but unanswered fields remain blank.

## Build Comparison EDA Notebook

```powershell
python build_comparison_eda_notebook.py
```

The notebook is written to:

`data/obesity_questionnaire_10_persona_comparison/with_without_background_comparison_eda.ipynb`

## Method

The flow intentionally follows the stronger `real_individual_pipeline` logic:

1. Build a grounded seed context from the CFPS row.
2. Ask the model to create a vivid, coherent persona first.
3. Ask the model to fully pretend to be that persona while answering the questionnaire.
4. Log all prompts, raw responses, token counts and runtime fields.

The prompt keeps hard facts fixed: age, gender, height, weight, BMI, education, income proxy, disease/comorbidity, healthcare and payment clues. City tier, household income, prior weight-loss methods and GLP-1 history are treated as bounded persona-stage assumptions because they are not directly observable in the CFPS person file.
