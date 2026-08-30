# Online Drift Response

This evaluates saved Sinkhole telemetry in 60-second time order. It compares a one-sided CUSUM on low-rank RPL state with DDM on errors from a Blackhole-trained CART model.

CUSUM uses no labels or attack markers. DDM receives delayed labels because it monitors classifier errors. The matching Blackhole seed is left out of both calibration and model training for each Sinkhole test seed.

This is online monitoring over recorded Cooja data. It does not retrain a classifier inside Contiki-NG.

```sh
python3 scripts/evaluate_online_drift_response.py
```
