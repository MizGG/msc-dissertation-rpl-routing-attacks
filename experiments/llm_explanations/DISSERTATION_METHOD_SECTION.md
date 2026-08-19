# LLM-Based Alert Explanation Method

## Purpose

The explanation layer is evaluated as a post-detection component rather than as
an IDS. Its purpose is to translate a routing-aware alert into a concise account
of what changed, which RPL mechanism may explain the change, what remains
uncertain and which verification action an analyst should take. The LLM does not
alter the IDS prediction, drift alarm or adaptation decision.

## Evidence Boundary

Each explanation request is generated from the first CUSUM alarm in each of the
five held-out sinkhole runs. Inputs contain the 60-second window, CUSUM value and
decision limit, observed generic RPL state, matched control state and aggregate
static-versus-adapted IDS performance. The routing evidence includes minimum
non-root rank, low-rank receiver/sender pairs, unique low-rank senders, exposed
receivers, received low-rank DIO count and parent-switch count.

Attack labels, activation messages, attacker identity, hidden evaluation ground
truth and attack-specific log markers are excluded from model-facing evidence.
This separation prevents the explanation from merely repeating a supplied
sinkhole label and tests whether it can connect observable routing state to a
plausible mechanism.

## Prompt Constraint

The system instruction requires valid JSON with six fields: `summary`,
`observed_change`, `likely_mechanism`, `confidence`, `limitations` and
`recommended_action`. The model is told to use only supplied evidence,
distinguish observations from inference, avoid inventing node identities or
packet loss and describe the mechanism as likely rather than proven. A fixed
model version and generation configuration should be used for all cases when
the live evaluation is run.

## Evaluation

Each response is scored from zero to two on four dimensions:

1. Evidence fidelity: whether the explanation accurately reports the rank,
   low-rank pair and CUSUM evidence.
2. Mechanism alignment: whether it connects the evidence to RPL rank
   manipulation or sinkhole-like parent attraction.
3. Uncertainty calibration: whether it marks the mechanism as an inference and
   avoids claims of certainty.
4. Actionability: whether it recommends a concrete verification or containment
   step supported by the evidence.

The maximum score is eight. The evaluation also reports JSON-validity rate and
unsupported-claim rate. Hidden rubrics contain the controlled attack identity
for scoring only and are never passed to the explaining model.

## Validity Limits

The five cases share one topology, one attack implementation and one feature
extraction design. They can demonstrate evidence fidelity and consistency but
cannot establish general explanation quality across deployments or attack
families. The handcrafted fixture validates the software schema and scorer; it
is not an LLM output and must not be reported as model performance. Any live LLM
results must preserve the raw response, exact model identifier, generation
settings and evaluation output for reproducibility.
