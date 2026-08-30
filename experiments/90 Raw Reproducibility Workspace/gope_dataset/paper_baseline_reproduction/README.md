# Reproducible Gope Static Baseline

Run with:

```sh
python3 scripts/reproduce_gope_paper_baseline.py
```

The script reads the eight supplied attack CSVs from the dissertation dataset
folder. For each family it uses `TYPE`, or `Node_Type` for Worst Parent, then
selects six features using Random Forest importance fitted on training data.
It evaluates Decision Tree and Random Forest models on both stratified random
and source-order 70/30 splits.

The source-order results exactly reproduce the previously preserved temporal
result table. They are an external static baseline, not a claim to reproduce
the paper's full adversarial reinforcement-learning or online-adaptation
pipeline. The raw data has no simulation-run identifier, so its rows cannot be
split by independent run.
