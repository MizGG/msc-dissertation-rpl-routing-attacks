# Sinkhole Defence V1

This separate Cooja experiment evaluates a narrow rank-consistency defence.
Enabled non-root motes reject a parent candidate that advertises the DODAG
root's minimum rank but does not have the DODAG root's interface identifier.

The campaign contains five matched seeds for control, Sinkhole attack, and
Sinkhole attack with defence. It is not a general trust framework or a claim of
cryptographic identity verification.

The final result is a negative mitigation finding: the prototype sees forged
minimum-rank advertisements but introduces unacceptable parent churn and radio
overhead. See `results_summary.md`; this package must be presented as a
bounded defence prototype, not a successful routing defence.
