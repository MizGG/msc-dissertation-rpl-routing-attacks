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

This framing is important for academic defensibility. The dissertation can
argue that the experiment reproduces a realistic problem for IoT IDS systems:
models are often trained on known attack behaviours, but deployed networks may
later face attacks that affect different protocol mechanisms. The work does not
need to prove that drift occurred spontaneously; it shows how performance
changes when drift is introduced in a controlled and repeatable way.

## External Dataset Interpretation

The external dataset strengthens the work by showing that the baseline IDS
pipeline performs well on supplied 6LoWPAN/RPL attack data. However, it should
not be used to overclaim the drift contribution. The external dataset mainly
supports reproducibility and baseline credibility, while the Cooja simulations
support the controlled drift, adaptation and Sybil contribution.

## Why Adaptation Helps

Adaptation improves performance because the model receives examples of the new
target-family behaviour. The whole-seed split makes this result more defensible
than random row splitting because the evaluation windows come from simulations
not used for adaptation.

The adaptation curve is more informative than a single retraining result. It
shows how much target-environment data is required before the IDS recovers.

The result should still be described as partial recovery rather than a complete
solution. Adaptation performs strongly when the target evidence exposes the
changed mechanism in the available features. Where the mechanism is subtle or
weakly represented, retraining may not be enough. This is the main lesson from
the earlier sinkhole concern: the problem is not just model updating, but the
relationship between model updating and feature representation.

## Why Some Attacks Transfer Poorly

Different attacks affect different mechanisms. Blackhole and grayhole are
forwarding attacks. Sinkhole and increase-rank affect routing rank. DIS flood,
DIO suppression and Sybil affect control-plane behaviour. Worst-parent affects
route choice. Wormhole affects topology plausibility.

Because the mechanisms differ, a feature set learned from one attack may not
capture the strongest signal from another. This explains why static models
trained on one family often fail under cross-attack evaluation.

This is also why accuracy alone is a weak summary for this dissertation. A
model can look acceptable overall while still having zero attack recall in a
changed environment. Recall, F1 and the confusion matrix are therefore central
to the argument because missed attacks are the operational failure mode.

## Sybil Contribution

Sybil is valuable because it is not just another packet-dropping or rank-change
attack. It introduces identity manipulation into the RPL control plane. The
result shows that the IDS can struggle when the attack surface changes, but that
limited Sybil adaptation data can restore high detection performance.

This gives the dissertation a clearer original extension beyond reproducing the
existing attack families.

The contribution should be stated precisely: the project implements and
evaluates a Sybil-style identity manipulation in the Cooja/RPL-lite setting and
uses it as a new drift target. It should not overclaim cryptographic identity
compromise or a complete Sybil defence. The value is that it broadens the
experimental attack surface and tests whether the IDS can adapt when the
observed mechanism shifts from routing/forwarding behaviour to identity-related
control-plane behaviour.

## Trust Layer Interpretation

The trust layer should be presented carefully. It does not currently improve IDS
metrics, so it should not be claimed as a solved defence. Its value is
interpretability: it helps describe which attack surface is suspicious.

This negative result is useful because it shows that adding trust scores is not
automatically enough. If trust scores are derived from existing features, they
may not add new predictive information. A stronger trust defence would need to
alter RPL parent selection online or add new evidence such as identity binding,
timing plausibility or neighbour-level observations.

This is a useful dissertation discussion point rather than a failure. It shows
critical analysis of the proposed defence layer: forwarding trust is naturally
suited to blackhole and grayhole behaviour, but weaker for attacks such as
wormhole and Sybil unless combined with timing, topology or identity evidence.

## LLM Explanation Role

The LLM layer is useful only if it is grounded. Its role is to explain IDS,
drift, adaptation and trust evidence to an analyst. It should not be presented
as an autonomous detector or as a replacement for the IDS.

The strongest LLM claim is about explanation quality: whether the model can
faithfully report supplied evidence, connect it to a plausible mechanism,
describe uncertainty and avoid hallucinating unsupported network events.
