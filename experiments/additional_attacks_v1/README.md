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
| DIO suppression | No implementation. | Suppresses outgoing DIO after 240 seconds; five matched Cooja seed pairs passed. |
| Worst parent | No implementation. | Selects the highest-rank acceptable parent after 240 seconds; five matched Cooja seed pairs passed. |
| Wormhole | No implementation. | Two colluding endpoints in a 17-mote directed-radio topology; five matched Cooja seed pairs passed. |
| Replay | No implementation. | Requires a safe control-message replay model and duplicate-handling instrumentation. |

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
| DIO suppression | 1-2 suppressed DIO outputs per run | 0 |
| Worst parent | 2,630-3,593 parent selections per run | 0 |
| Wormhole | 1,706-1,725 endpoint-link radio events per run | 0 |

The configurations are generated from the already validated 16-mote topology
using `generate_configs.py`; wormhole configurations are generated separately
with `generate_wormhole_configs.py` because they use 17 motes and a directed
radio graph. The complete five-attack/five-control-seed batch passed
`validate_runs.py` for each implemented family.

`contiki_snapshots/` preserves the exact live `uip6.c`, `rpl-icmp6.c` and
`rpl-neighbor.c` used by this package. The grayhole hook is in `uip6.c`; it
drops every second forwarded packet only while `grayhole_attack_enabled` is
set. Existing blackhole, sinkhole and increase-rank hooks remain present and
unchanged.
