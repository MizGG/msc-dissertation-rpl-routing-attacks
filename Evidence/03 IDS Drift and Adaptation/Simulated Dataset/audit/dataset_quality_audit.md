# Dataset Quality Audit v1

**Status:** PASS

## Integrity

- 810 rows, 84 columns, and 90 complete run groups.
- Nine attack families; each contributes 90 windows (45 attack and 45 control).
- No empty values, non-numeric feature values, duplicate run windows, or incomplete 60-second sequences were found.

## Labels And Timing

- Every group contains windows starting at 0, 60, ..., 480 seconds.
- `window_label=1` only for attack-run windows beginning at or after the 240-second activation boundary.
- Control windows and pre-activation attack windows are labelled 0.

## Leakage Control

- 16 attack-implementation marker fields are validation-only and excluded from IDS features.
- 57 numeric generic features remain eligible before a model-specific feature selection step.
- `family`, `seed`, run IDs, labels, and time fields are metadata and are also excluded from model inputs.

## Generic Feature Range Check

- `app_tx_delta`: 0.0 to 140.0
- `app_rx_delta`: 0.0 to 140.0
- `app_missed_delta`: 0.0 to 6.0
- `radio_tx_count`: 352.0 to 11863.0
- `dio_rx_count`: 0.0 to 356.0
- `dio_tx_count`: 0.0 to 103.0
- `dis_rx_count`: 0.0 to 53.0
- `dao_rx_count`: 0.0 to 15.0
- `parent_switch_count`: 0.0 to 54.0
- `dio_rx_low_rank_nonroot_count`: 0.0 to 25.0
- `state_low_rank_nonroot_pairs`: 0.0 to 5.0
- `own_rank_mean`: 256.0 to 22289.6667

## Evaluation Protocol

- Split only by complete family/mode/seed groups; never random CSV rows.
- For cross-attack drift, train on one family and hold out all target-family groups.
- For adaptation, use complete target seeds for adaptation and evaluate only on different target seeds.
- Use marker fields only to verify attack activation, never as IDS or drift-detector input.
