# External Gope Temporal Reproduction

This directory preserves result tables generated earlier from the supplied Dr
Gope dataset. The original work remains at:

`/Users/mizzy/Documents/Dissertation/recreation/using real dataset/`

The source script used the actual labelled attack CSVs and, for each attack
family, trained on the first 70 percent of source-file rows and evaluated on the
last 30 percent. It selected six features using training-only Random Forest
importance, then evaluated a depth-limited Decision Tree and Random Forest.

This is a within-family temporal/order split, not a simulation-run split and not
a blackhole-to-sinkhole transfer experiment. It is therefore supporting external
validation only. The Cooja seed-separated blackhole-to-sinkhole results remain
the primary concept-drift evidence.

The copied CSV files have SHA-256 values:

- `actual_dataset_temporal_split_results.csv`: `201ccb5c8d840e764206b29a7bbd674c35ee86c31c052802d00fdc4de3ac91e0`
- `selected_top6_features_temporal_split.csv`: `643f91099462455b3b0a4447b464d3f3186bd10110fe5f884bb605f851e6f869`

The important external comparison is that the selected feature sets include
RPL-aware fields such as `Source_Rank`, `Parrent_Node`, `Src_DIS_count`,
`Src_DIO_count`, `Parents_Count` and `CHILD_COUNT`. This supports, but does not
prove, the routing-feature design used in the Cooja experiment.
