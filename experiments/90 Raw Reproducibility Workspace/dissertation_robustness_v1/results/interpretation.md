# Online Monitoring and Uncertainty Interpretation

## Online Monitoring Comparison

On the five seed-separated blackhole-to-sinkhole Cooja streams, the rank-state
CUSUM alarmed in all five attack runs at the 240-second activation window. It
does not use labels or attack markers as inputs. DDM, applied to delayed errors
from the blackhole-trained CART model, also alarmed in all five attack runs but
at 300 seconds because one 60-second label delay is intentionally modelled.
Neither detector alarmed in the five matched control runs.

This does not show that CUSUM is universally superior to DDM. The two detectors
observe different evidence: CUSUM observes the changed RPL state directly,
whereas DDM observes the static IDS failing after delayed labels become
available. The data are deliberately simple and the CUSUM features are tuned to
persistent low non-root rank, so the comparison is a mechanism-aware case study
rather than a broad drift-detector benchmark.

## Seed-Level Variation

The routing-aware CART adaptation result remains strong but is not uniform. With
one target sinkhole seed, F1 spans 0.5714 to 1.0000 across the five possible
adaptation seeds. With three target seeds, F1 spans 0.8889 to 1.0000 across ten
overlapping seed combinations. This variation should be shown or mentioned,
not hidden behind a mean value.

The detector's observed 5/5 attack detection rate has a Wilson 95% interval of
0.5655 to 1.0000; its observed 0/5 control false-alarm rate has an interval of
0.0000 to 0.4345. This wide uncertainty is expected for five runs and prevents
a deployment-level claim.

## Dissertation-Ready Wording

> In the controlled blackhole-to-sinkhole stream, a label-free rank-state CUSUM
> identified all five sinkhole activations in the first 60-second post-activation
> window. A DDM monitor over delayed static-IDS errors also identified all five
> changes one window later. The small seed count produces wide confidence
> intervals, so these findings demonstrate controlled simulation behaviour rather
> than field-deployment performance.
