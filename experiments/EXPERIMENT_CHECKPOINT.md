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

Summary:

| Experiment | Accuracy | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: |
| Blackhole same-family validation | 1.00 | 1.00 | 1.00 | 1.00 |
| Train on blackhole, test on sinkhole | 0.50 | 0.00 | 0.00 | 0.00 |

Interpretation:

The detector learns the blackhole attack pattern under same-family evaluation, but fails to identify sinkhole attacks when the attack distribution changes. This is the current concept-drift demonstration.

## Immediate Next Work

1. Keep the simulation stage frozen temporarily.
2. Write the dissertation experiment method and result section from the existing evidence.
3. Add a small adaptation experiment: train on blackhole first, then retrain or update with sinkhole runs and compare static vs adapted performance.
4. Add explanation output only after the static-vs-adapted drift result is stable.

## Git Hygiene

Cooja build outputs under `build/cooja/` are ignored for future generated files. Existing tracked build artefacts may still appear as modified after local builds; they are not part of the scientific evidence package.
