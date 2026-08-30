# Frozen Simulated Dataset

This is the main Cooja dataset used for IDS, cross-attack drift and adaptation analysis. It has 810 labelled 60-second windows from nine attack families.

Each family has five attack runs and five matched controls. Runs last 540 seconds; attacks start at 240 seconds. Attack windows from 240 seconds onward are labelled malicious.

- `data/cooja_rpl_baseline_windows_v1.csv` contains the windows.
- `data/cooja_rpl_baseline_run_manifest_v1.csv` records their source runs.
- `data_dictionary.md` describes the fields.
- `evaluation_protocol.md` records the split rule.

Keep every `family:mode:seed` group together during training and evaluation. The robustness and defence campaigns are not included in this baseline dataset.

To rebuild the dataset:

```sh
python3 experiments/final_simulated_dataset_v1/build_dataset.py
```
