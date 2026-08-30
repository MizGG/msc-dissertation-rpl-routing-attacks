# Weak-Flag Diagnostic Evidence

These ten sinkhole runs were generated with the original weak-only
`sinkhole_attack_enabled` definition. Generic INFO telemetry showed that node
16 advertised rank 128 once at 240.473 seconds, but subsequent DIOs reverted to
the real rank 256. The original activation marker alone did not expose this
loss of persistent attack state.

The runs and their first extracted feature/results tables are retained here as
diagnostic evidence. They are excluded from the final routing-feature IDS
dataset. The corrected experiment gives the sinkhole router and control
firmware a strong flag definition while leaving the RPL advertisement hook
unchanged.
