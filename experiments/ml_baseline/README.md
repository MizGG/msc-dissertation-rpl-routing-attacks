# Baseline IDS Results

Pure-Python random forest over complete-run traffic features from `experiments/features/run_level_features.csv`.

Attack-marker fields such as sinkhole advertised-rank events and blackhole log counts are excluded from training to avoid label leakage.

The main drift row is `concept_drift_train_blackhole_test_sinkhole`: a model trained on blackhole/control runs is evaluated on sinkhole/control runs.

`adaptation_curve.csv` and `adaptation_summary.csv` evaluate recovery after adding whole sinkhole seeds to the training set. Evaluation always uses sinkhole seeds that were not used for adaptation.

`feature_diagnostics.csv` compares attack/control feature means by attack family and helps explain whether the run-level feature set captures each attack mechanism.
