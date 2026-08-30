# Conclusion

This project created a reproducible Cooja-based RPL IDS evaluation with nine
attack families, 90 validated baseline runs, and a frozen 810-window dataset.
Sybil extended the campaign into identity-related RPL control-plane behaviour.

Static cross-attack transfer was poor: CART produced zero attack recall in 48
of 72 pairs and mean F1 of 0.1823. Whole-seed adaptation and online rank-state
monitoring recovered performance in many controlled conditions, but robustness
tests showed that topology and radio changes can also harm static decisions.

The sinkhole defence experiment established a necessary boundary: useful rank
telemetry does not justify blunt parent-selection intervention. The contribution
is a controlled framework for exposing transfer failures, testing seed-safe
adaptation, and evaluating identity manipulation without overstating evidence.
