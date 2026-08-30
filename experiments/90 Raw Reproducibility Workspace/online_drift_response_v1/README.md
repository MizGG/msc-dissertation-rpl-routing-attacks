# Online Drift Response V1

This package makes the Cooja blackhole-to-sinkhole analysis more explicit about
what is and is not online.

Each 60-second sinkhole run is processed in time order. The evaluation compares:

- a one-sided CUSUM over generic persistent low-rank RPL state; and
- DDM over errors from a blackhole-trained CART IDS, with one-window delayed
  labels.

CUSUM receives no labels or attack markers. DDM is a supervised detector, so it
receives the delayed ground-truth label only after the prediction it evaluates.
Neither detector receives implementation markers.

The matching blackhole seed is excluded from the CUSUM calibration and CART
training for each sinkhole seed. This avoids using same-seed source data in the
evaluation fold.

## Scope

This is an online *monitoring* evaluation over saved Cooja telemetry. It does
not yet perform autonomous live retraining inside Contiki-NG. The existing
whole-seed adaptation curves remain the valid evaluation of retraining after
representative target-family evidence is available. A future live system would
need a label-acquisition policy, retraining budget and safety checks before
changing its active classifier.

## Reproduce

```bash
python3 scripts/evaluate_online_drift_response.py
```

## Interpretation Rules

- Compare CUSUM and DDM as different sensors, not interchangeable algorithms.
- Do not claim DDM is unsupervised: it needs delayed labels through IDS errors.
- Do not claim either result proves field deployment performance.
- Report the fixed 60-second window granularity when discussing detection delay.
