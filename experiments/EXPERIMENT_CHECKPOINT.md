# Experiment Checkpoint

Date: 2026-08-19

## Current Research Thread

The Cooja work is being used as controlled data generation for an MSc cybersecurity and AI dissertation on IDS behaviour under concept drift in RPL/6LoWPAN networks.

The current experimental chain is:

```text
Contiki-NG / Cooja RPL simulations
-> matched attack and control runs
-> run-level traffic features
-> baseline IDS
-> cross-attack concept drift evaluation
```

## Completed Evidence

### Blackhole

Final evidence package:

`experiments/blackhole/final_corrected_240s_540s/`

Properties:

- 16-node topology
- 5 attack seeds and 5 matched control seeds
- attack activation at 240 seconds
- simulation duration 540 seconds
- preserved source, configs, logs, run directories, validation summary and SHA256 manifest

### Sinkhole

Final evidence package:

`experiments/sinkhole/final_corrected_240s_540s/`

Properties:

- 16-node topology
- 5 attack seeds and 5 matched control seeds
- attack activation at 240 seconds
- simulation duration 540 seconds
- attacker advertises attractive low RPL rank while preserving its internal rank
- preserved source, configs, logs, run directories, validation summary and SHA256 manifest

### Feature Dataset

Run-level feature table:

`experiments/features/run_level_features.csv`

Properties:

- 20 complete simulation runs
- 10 blackhole-family runs
- 10 sinkhole-family runs
- whole-run rows, avoiding row-level leakage across train/test splits

### Baseline IDS

Baseline output:

`experiments/ml_baseline/baseline_results.csv`

Adaptation outputs:

- `experiments/ml_baseline/adaptation_curve.csv`
- `experiments/ml_baseline/adaptation_summary.csv`
- `experiments/ml_baseline/feature_diagnostics.csv`
- `experiments/ml_baseline/adaptation_interpretation.md`
- `experiments/features/window_features.csv`
- `experiments/ml_window/window_results.csv`
- `experiments/ml_window/window_adaptation_summary.csv`
- `experiments/ml_window/window_feature_interpretation.md`

Summary:

| Experiment | Accuracy | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: |
| Blackhole same-family validation | 1.00 | 1.00 | 1.00 | 1.00 |
| Train on blackhole, test on sinkhole | 0.50 | 0.00 | 0.00 | 0.00 |

Interpretation:

The detector learns the blackhole attack pattern under same-family evaluation, but fails to identify sinkhole attacks when the attack distribution changes. This is the current concept-drift demonstration.

The first adaptation experiment adds whole sinkhole seeds to training and evaluates on held-out sinkhole seeds. F1 remains 0.00 after adding up to three sinkhole seeds, indicating that the current coarse run-level features do not represent sinkhole rank manipulation well enough for recovery.

The follow-up 60-second window experiment improves the time representation. Blackhole windows remain detectable in-domain, but a frozen blackhole-trained model still has 0.00 sinkhole recall. With three sinkhole adaptation seeds, sinkhole recall reaches 1.00 but precision remains low, showing a recovery/false-positive tradeoff rather than clean adaptation.

### Supplied Gope Dataset

Audit outputs:

- `experiments/gope_dataset/audit_summary.csv`
- `experiments/gope_dataset/column_overlap.csv`
- `experiments/gope_dataset/missing_values.csv`
- `experiments/gope_dataset/paper_alignment.md`
- `experiments/gope_dataset/gope_baseline_results.csv`

The supplied `DR P` folder contains 768,811 rows across eight attack CSVs. Seven files have 71 columns and a `TYPE` label; Worst Parent has 46 columns and no `TYPE` label. The seven labelled files contain routing-aware fields such as rank, parent, DIO/DAO/DIS counts, hop count and packet loss. A preliminary Gaussian baseline over sampled labelled Gope data gives high precision but low recall, and a Gope blackhole-to-sinkhole test also has poor sinkhole recall.

## Immediate Next Work

1. Keep the simulation stage frozen temporarily.
2. Write the dissertation experiment method and result section from the existing evidence.
3. Improve feature extraction for sinkhole-specific behaviour using temporal-window, routing-parent, rank, DIO/DAO, or topology-change features.
4. Reproduce a stronger Gope baseline with a better model and documented preprocessing.
5. Re-run static, drift, and adaptation experiments with improved Cooja routing features.
6. Add explanation output only after the feature representation and drift/adaptation result are stable.

## Git Hygiene

Cooja build outputs under `build/cooja/` are ignored for future generated files. Existing tracked build artefacts may still appear as modified after local builds; they are not part of the scientific evidence package.
