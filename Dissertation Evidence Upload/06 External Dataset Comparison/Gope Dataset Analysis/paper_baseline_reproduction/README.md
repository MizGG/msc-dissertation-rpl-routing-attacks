# Gope Static Baseline

Run:

```sh
python3 scripts/reproduce_gope_paper_baseline.py
```

The script reads the eight supplied attack CSVs, selects six training-only features with Random Forest importance, and evaluates Decision Tree and Random Forest models using random and source-order 70/30 splits.

The source-order table reproduces the stored temporal result table. It is a static external baseline, not a recreation of the full adversarial-RL or online-adaptation architecture. The supplied rows have no simulation-run identifier, so independent-run splits are not possible.
