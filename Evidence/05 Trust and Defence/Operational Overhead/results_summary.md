# Operational Overhead Result

## Scope

All values are post-activation means across the five matched Cooja seeds in the
sinkhole-defence campaign. The comparison is deliberately narrow: it evaluates
the rank/parent intervention prototype, not a production-ready RPL defence.

## Result

The unmitigated sinkhole condition was almost indistinguishable from the
control for this application workload: mean responses were 416.6 versus 417.4
(-0.19%) and mean radio transmissions were 5,242.6 versus 5,217.4 (+0.48%).
This does not mean the rank manipulation was harmless: it was visible in the
routing telemetry, with 40 mean non-root minimum-rank DIO events per run.

The prototype rank-parent defence produced an unacceptable operational cost.
It reduced mean application responses from 417.4 to 87.4 (-79.06%), generated
28.8 missed responses and 681.8 parent switches per run, and increased mean
radio transmissions from 5,217.4 to 35,020.0 (+571.2%). The defence logged a
mean of 9,702.2 avoidance decisions per run.

## Defensible Interpretation

The result is negative but useful. Rank evidence is informative for detection
and drift analysis, whereas directly forcing parent selection from a simple
minimum-rank rule destabilises the routing process in this topology. The
prototype must not be presented as a successful mitigation.

A future defence needs confidence aggregation, hysteresis, a recovery path,
and an overhead evaluation that includes an appropriate mote energy model or a
physical deployment. This project makes no energy, ROM/RAM, or physical-testbed
claim from these Cooja native-target results.
