# Additional RPL Attack Workstream

This package is separate from the validated blackhole and sinkhole evidence.
It is the workspace for bringing additional attacks to the same standard:
delayed activation at 240 seconds, matched control firmware, five fixed seeds,
540-second Cooja simulations, raw logs, validation and feature extraction.

## Current Status

| Attack | Existing state | This package |
| --- | --- | --- |
| DIS flooding | Earlier immediate attacker and manual 16-/17-mote configurations exist. | Delayed attacker/control firmware; five matched Cooja seed pairs passed. |
| Grayhole | No implementation. | Deterministic 50% forwarding-drop hook, firmware and five matched Cooja seed pairs passed. |
| Increase rank | RPL advertised-rank hook exists. | Strong-flag firmware and five matched Cooja seed pairs passed. |
| Wormhole | No implementation. | Requires two colluding motes and an explicit tunnel design. |
| DIO suppression | No implementation. | Requires a DIO-output suppression hook and validation of normal internal rank. |
| Replay | No implementation. | Requires a safe control-message replay model and duplicate-handling instrumentation. |
| Worst parent | No implementation. | Requires an objective-function or parent-selection intervention. |

No attack is reported as completed until it has a matched control, Cooja run
evidence and validation output. The blackhole and sinkhole packages must not be
modified while this workstream is developed.

## Smoke Validation

All five fixed seeds completed for each attack and control condition. The
resulting `validation_summary.csv` records the following post-activation effects:

| Attack | Attack effect events | Control effect events |
| --- | ---: | ---: |
| DIS flooding | 149 multicast DIS transmissions per run | 0 |
| Grayhole | 208-211 forwarded packet drops per run | 0 |
| Increase rank | 1-2 advertised-rank manipulations per run | 0 |

The configurations are generated from the already validated 16-mote topology
using `generate_configs.py`. The complete five-attack/five-control-seed batch
passed `validate_runs.py` for each family.

`contiki_snapshots/` preserves the exact live `uip6.c` and `rpl-icmp6.c` used
by this package. The grayhole hook is in `uip6.c`; it drops every second
forwarded packet only while `grayhole_attack_enabled` is set. Existing
blackhole, sinkhole and increase-rank hooks remain present and unchanged.
