# Cross-Attack Adaptation Curves

This experiment extends the cross-attack concept-drift matrix by asking whether
the IDS recovers after seeing a small amount of data from the new target attack
family.

For each source attack and target attack pair:

1. Train on all source-family attack/control windows.
2. Add 0, 1, 2 or 3 whole target seeds as adaptation data.
3. Test only on target seeds that were not used for adaptation.

The primary run uses the CART model and 57 non-marker routing/window features.
Simulator attack-marker features are excluded to avoid leaking implementation
markers into the IDS.

## Outputs

- `cross_attack_adaptation_curves.csv`: every source-target adaptation
  evaluation.
- `cross_attack_adaptation_summary.csv`: compact source-target summary by
  adaptation seed count.

## Headline Result

Across the 56 cross-attack source-target pairs:

| Target seeds used for adaptation | Mean recall | Mean F1 |
| ---: | ---: | ---: |
| 0 | 0.2250 | 0.1674 |
| 1 | 0.7875 | 0.8056 |
| 2 | 0.8583 | 0.8566 |
| 3 | 0.8911 | 0.8701 |

This supports the adaptation argument: static cross-attack models often fail
under concept drift, but limited target-environment observations can recover
substantial detection performance.

## Remaining Failure Modes

Adaptation does not fix everything. With three target seeds, several
source-to-DIO-suppression cases still fail or remain weak:

| Source -> target | Recall | F1 | FPR |
| --- | ---: | ---: | ---: |
| dis_flood -> dio_suppression | 0.0000 | 0.0000 | 0.0000 |
| grayhole -> dio_suppression | 0.0000 | 0.0000 | 0.0000 |
| worst_parent -> dio_suppression | 0.0000 | 0.0000 | 0.0000 |
| increase_rank -> dio_suppression | 0.1000 | 0.1818 | 0.0000 |

This is useful dissertation evidence. It shows that adaptation is not merely
"add more data and the problem disappears". Some attack mechanisms remain hard
under the current routing-window representation, so feature design and
mechanism-aware monitoring matter.

## Method Note

This run uses a deterministic seed subset for speed: the first 1, 2 or 3 target
seeds are used for adaptation and the remaining target seeds are held out. The
script also supports exhaustive seed-combination evaluation with
`--split-mode all_combinations`, but that is slower and was not used for this
first broad result.
