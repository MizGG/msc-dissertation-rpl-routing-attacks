# Discussion

## Concept Drift Interpretation

The central result is that attack evolution causes a meaningful change in the
feature distribution seen by the IDS. A classifier trained on one attack family
often fails when tested on another. The failure is clearest in zero-recall
cross-attack pairs, where the model does not identify any attack windows in the
new environment.

This should be described as a controlled attack-distribution change used to
evaluate concept drift. The experiment does not claim to observe naturally
occurring drift in a deployed network. Instead, it constructs drift by changing
the attack mechanism while keeping the simulation framework controlled.

## Why Adaptation Helps

Adaptation improves performance because the model receives examples of the new
target-family behaviour. The whole-seed split makes this result more defensible
than random row splitting because the evaluation windows come from simulations
not used for adaptation.

The adaptation curve is more informative than a single retraining result. It
shows how much target-environment data is required before the IDS recovers.

## Why Some Attacks Transfer Poorly

Different attacks affect different mechanisms. Blackhole and grayhole are
forwarding attacks. Sinkhole and increase-rank affect routing rank. DIS flood,
DIO suppression and Sybil affect control-plane behaviour. Worst-parent affects
route choice. Wormhole affects topology plausibility.

Because the mechanisms differ, a feature set learned from one attack may not
capture the strongest signal from another. This explains why static models
trained on one family often fail under cross-attack evaluation.

## Sybil Contribution

Sybil is valuable because it is not just another packet-dropping or rank-change
attack. It introduces identity manipulation into the RPL control plane. The
result shows that the IDS can struggle when the attack surface changes, but that
limited Sybil adaptation data can restore high detection performance.

This gives the dissertation a clearer original extension beyond reproducing the
existing attack families.

## Trust Layer Interpretation

The trust layer should be presented carefully. It does not currently improve IDS
metrics, so it should not be claimed as a solved defence. Its value is
interpretability: it helps describe which attack surface is suspicious.

This negative result is useful because it shows that adding trust scores is not
automatically enough. If trust scores are derived from existing features, they
may not add new predictive information. A stronger trust defence would need to
alter RPL parent selection online or add new evidence such as identity binding,
timing plausibility or neighbour-level observations.

## LLM Explanation Role

The LLM layer is useful only if it is grounded. Its role is to explain IDS,
drift, adaptation and trust evidence to an analyst. It should not be presented
as an autonomous detector or as a replacement for the IDS.

The strongest LLM claim is about explanation quality: whether the model can
faithfully report supplied evidence, connect it to a plausible mechanism,
describe uncertainty and avoid hallucinating unsupported network events.

