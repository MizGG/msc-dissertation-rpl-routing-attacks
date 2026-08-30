# Cross-Attack Adaptation With Sybil

The source model is trained on one attack family, then updated with 0-3 complete target-family seeds. Evaluation always uses target seeds that were not used for adaptation. Rows were never split randomly.

| Target seeds used for adaptation | Mean recall | Mean F1 |
|---|---:|---:|
| 0 | 0.2333 | 0.1822 |
| 1 | 0.8056 | 0.8258 |
| 2 | 0.8620 | 0.8664 |
| 3 | 0.8917 | 0.8792 |

For Sybil as the target, mean F1 rose from 0.2183 with no target data to 0.9683 with one target seed. This is why the dissertation treats adaptation as exposure to representative new behaviour, not as a random-row retraining exercise.
