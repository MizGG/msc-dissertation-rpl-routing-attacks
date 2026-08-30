# Robustness and Scope Package V1

This package adds uncertainty reporting and an explicit comparison of the
dissertation methodology with the two anchor papers. It does not alter Cooja
attack configurations or the preserved final evidence packages.

## Outputs

- `results/adaptation_seed_spread.csv`: mean, standard deviation and range
  across whole-seed adaptation splits. These splits overlap, so this is spread,
  not an independent confidence interval.
- `results/detector_rate_uncertainty.csv`: Wilson 95% intervals over the five
  attack and five control runs for each detector.
- `methodology_comparison_and_limitations.md`: wording suitable for the
  dissertation and presentation.
- `results/interpretation.md`: bounded interpretation of the detector and
  adaptation results.

## Reproduce

```bash
python3 scripts/evaluate_online_drift_response.py
python3 scripts/summarize_seed_uncertainty.py
```
