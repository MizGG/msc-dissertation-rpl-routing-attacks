# Cross-Attack Adaptation With Sybil

This experiment repeats the whole-seed adaptation curve after adding Sybil as a
ninth attack family. The model is trained on a source attack/control family,
then given 0-3 whole target-family seeds for adaptation and evaluated only on
held-out target seeds.

The split is by simulation seed, not random rows, to avoid leakage between
training and evaluation.

## Overall Mean CART Results

| Target adaptation seeds | Mean recall | Mean F1 |
| --- | ---: | ---: |
| 0 | 0.2333 | 0.1822 |
| 1 | 0.8056 | 0.8258 |
| 2 | 0.8620 | 0.8664 |
| 3 | 0.8917 | 0.8792 |

## Sybil As Target

| Sybil adaptation seeds | Mean recall | Mean F1 |
| --- | ---: | ---: |
| 0 | 0.2750 | 0.2183 |
| 1 | 0.9437 | 0.9683 |
| 2 | 0.9333 | 0.9616 |
| 3 | 0.9500 | 0.9688 |

Interpretation: Sybil is a useful new attack surface for the dissertation. A
static IDS trained on other attacks often misses it, but limited whole-run
adaptation restores strong detection performance. That supports the core claim
that attack evolution causes distribution shift, and that recovery depends on
exposing representative examples of the new behaviour.
