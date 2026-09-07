# Data Dictionary

The dataset preserves the common 83-column routing-window schema already used
by the primary cross-attack analysis, plus `source_feature_file` for provenance.
The most important fields are:

| Field group | Meaning |
| --- | --- |
| `run_id`, `family`, `mode`, `seed`, `nodes` | Simulation provenance. |
| `window_start_s`, `window_end_s`, `post_activation` | Time-window context. |
| `binary_run_label` | Attack-run label; all windows from an attack run are 1. |
| `window_label` | IDS label: 1 only for an attack window at or after 240 seconds. |
| `app_*` | Application Tx/Rx/missed-Tx changes observed in the window. |
| `radio_*` | Cooja radio-event counts and bytes; these are not physical energy measurements. |
| `dio_*`, `dis_*`, `dao_*` | RPL control-plane activity and rank observations. |
| `parent_*`, `topology_*` | Parent selection and inferred routing-topology indicators. |
| `*_attack_enabled_events`, `*_events` | Simulator instrumentation markers retained for validation only. They must be excluded from primary IDS feature sets because they leak implementation ground truth. |

The full machine-readable column names are in the CSV header. The existing
feature-selection scripts define the marker exclusion used by the primary IDS
experiments.
