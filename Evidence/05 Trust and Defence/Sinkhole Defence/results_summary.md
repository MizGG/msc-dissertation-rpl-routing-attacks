# Sinkhole Defence V1 Results

## Design

The prototype monitors the RPL parent-selection path. When enabled, it treats
a non-root candidate advertising `ROOT_RANK` as suspicious. The final version
prefers to retain an existing safe parent or select an alternative safe parent;
it fails open when no safe alternative exists. It is deliberately limited to
the experiment's rank-128 Sinkhole mechanism.

## Matched Five-Seed Result

| Condition | Mean post-activation app responses | Mean parent switches | Mean radio transmissions |
| --- | ---: | ---: | ---: |
| Control | 417.4 | 0.0 | 5,217.4 |
| Sinkhole attack | 416.6 | 0.0 | 5,242.6 |
| Sinkhole plus defence | 87.4 | 681.8 | 35,020.0 |

The defended runs all completed, and the defence logged attempted avoidance of
suspicious root-rank candidates. However, the parent-selection intervention
caused severe route churn, greatly increased radio traffic, and reduced
application delivery. The unmitigated Sinkhole did not materially reduce
delivery in this topology, despite its visible forged-rank advertisements.

## Interpretation

This is a negative but useful result. A rank-only hard or soft parent filter is
not a safe standalone RPL defence in this topology. Rank evidence is valuable
for IDS representation and drift monitoring, but using it directly to alter
parent selection needs additional safeguards, such as confidence accumulation,
route-quality checks, hysteresis, and a separately evaluated recovery policy.

The strict hard-rejection and first alternative-parent variants are preserved
under `diagnostics/`. They are excluded from the final comparison because both
had worse churn and overhead. Do not claim that this package mitigates the
Sinkhole attack; present it as an evaluated prototype and design limitation.
