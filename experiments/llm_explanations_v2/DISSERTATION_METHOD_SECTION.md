# LLM Explanation Method

The LLM component is evaluated as a post-detection explanation layer rather
than as an intrusion detector. Cooja logs are first converted into routing
windows. The IDS and cross-attack drift experiments then produce static and
adapted model performance, while the trust layer produces interpretable
forwarding, rank, control-message and route trust indicators.

For each attack family, one post-activation window is selected from seed
`123456`. The selected window is the most informative post-activation window
under the available feature differences between the attack run and its matched
control run. The LLM receives structured evidence containing the window timing,
static cross-attack IDS context, adaptation context, feature deltas and trust
alerts.

The prompt instructs the model to use only the supplied evidence, distinguish
observation from inference, avoid inventing attacker identities or packet
captures and return valid JSON with:

- `summary`;
- `observed_change`;
- `likely_mechanism`;
- `drift_implication`;
- `confidence`;
- `limitations`;
- `recommended_action`.

Hidden evaluation rubrics are not included in the prompt. Each response is
scored on schema validity, evidence fidelity, mechanism alignment, uncertainty
calibration, drift alignment, actionability and unsupported claims. This tests
whether the model can explain IDS behaviour under concept drift without
hallucinating beyond the experimental evidence.

The LLM is therefore positioned as an analyst-support tool. It does not replace
the IDS, does not modify routing decisions and does not prove attack identity.

