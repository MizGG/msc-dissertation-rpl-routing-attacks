# Limitations

The research uses Cooja rather than a physical 6LoWPAN deployment. It does not
claim field-ready accuracy, calibrated energy use, mote ROM/RAM footprint, or
network lifetime. Cooja radio-event counts are activity proxies, not energy
measurements.

Five attack and five control seeds per family enable controlled matched
experiments but do not establish broad statistical generalisation. Robustness
tests cover relocation and lossy radio only, not mobility, workload changes,
topology scaling, collusion, or mixed attacks.

Feature representation constrains what adaptation can learn. Marker exclusion
strengthens validity but prevents models from exploiting simulator debug text.
The rank-parent intervention is a narrow prototype, not a secure-routing
protocol. External data have different run provenance and feature schemas, so
direct merging requires a compatibility audit.

A live LLM explanation experiment was deliberately omitted from empirical
claims because it needs reproducible settings and unsupported-claim analysis.
