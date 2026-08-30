# Frozen Simulated Dataset v1

This package freezes the primary baseline dataset used for the dissertation's
Cooja-based IDS, cross-attack drift, and whole-seed adaptation analyses. It
does not rerun simulations or alter raw logs.

## Contents

- `data/cooja_rpl_baseline_windows_v1.csv`: 810 labelled 60-second routing
  windows across nine attack families.
- `data/cooja_rpl_baseline_run_manifest_v1.csv`: one record per complete
  family/mode/seed group, retaining source-file provenance.
- `data/validation_summary.txt`: machine-checkable package validation result.
- `build_dataset.py`: standard-library-only reproducible exporter.

## Experimental Scope

Each family contains five attack and five matched control Cooja runs. Each run
contributes nine windows (0--60 through 480--540 seconds). Attacks activate at
240 seconds; a window is labelled malicious only for attack runs at or after
that boundary. The source extracts are listed in the run manifest.

The baseline package contains blackhole, sinkhole, DIS flooding, grayhole,
increase-rank, DIO suppression, worst-parent, wormhole, and Sybil. It excludes
the attacker-relocation, lossy-radio, and sinkhole-defence campaigns so that
the primary data distribution remains controlled and clearly defined.

## Split Rule

Never split CSV rows randomly. A whole `family:mode:seed` group must be kept on
one side of any train/test or adaptation split. For a target-family adaptation
experiment, target seeds used for adaptation must not appear in target test
groups.

## Reproduction

From the repository root, run:

```sh
python3 experiments/final_simulated_dataset_v1/build_dataset.py
```

The exporter requires only Python 3 standard-library modules and reads the
already validated feature extracts; no API key, network access, or Cooja run is
required.
