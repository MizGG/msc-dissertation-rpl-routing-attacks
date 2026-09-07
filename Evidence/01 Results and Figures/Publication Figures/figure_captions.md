# Figure Captions

**Cross-attack static IDS performance.** F1 of a CART IDS trained on the row
attack family and evaluated on the held-out column family. Explicit simulator
attack markers were excluded. The widespread low off-diagonal F1 demonstrates
that strong in-domain detection does not imply transfer to a changed attack
mechanism.

**Online drift detection.** Both monitors detected all five held-out sinkhole
attack runs and produced no false alarm on the five matched controls. The CUSUM
signal occurred in the first post-activation window; DDM, which consumes
delayed classification errors, alerted one 60-second window later.

**Robustness under condition shift.** Static CART performance was sensitive to
attacker relocation and lossy radio conditions. Incorporating three complete
target-condition seeds substantially restored held-out F1 in the affected
conditions. This is condition-specific adaptation, not proof of universal
deployment robustness.

**Sinkhole defence overhead.** The simple rank-parent intervention caused severe
routing churn and radio activity while reducing application responses. It is a
negative result and is not presented as a successful mitigation.
