# LLM Explanation Layer Summary

The LLM layer has been packaged as:

`experiments/llm_explanations_v2`

It is not an IDS. It receives structured evidence produced by the IDS,
cross-attack drift experiment, adaptation experiment and trust layer, then
generates a constrained explanation for a human analyst.

## What It Explains

For each of the nine attack families, the package selects a post-activation
window and supplies:

- static cross-attack IDS context;
- adaptation context;
- attack-vs-control feature deltas;
- trust alerts;
- top changed features.

The model-facing prompt excludes hidden ground-truth labels and simulator
attack markers.

## Evaluation

The scoring rubric checks:

- JSON schema validity;
- evidence fidelity;
- mechanism alignment;
- uncertainty calibration;
- drift awareness;
- actionability;
- unsupported claims.

The current scored outputs are fixtures used to validate the software and demo
pipeline. They are not reported as external live LLM performance.

## Presentation Position

The defensible dissertation claim is that the LLM provides an
evidence-grounded explanation layer for IDS behaviour under concept drift. It
does not detect attacks directly and should not be presented as replacing the
IDS.
