# Discussion

The main finding is static IDS brittleness, not an inability to detect every
RPL attack. A model trained on one narrow malicious mechanism frequently failed
when the mechanism changed. The 48 zero-recall CART pairs show why strong
in-domain scores cannot establish robust IDS behaviour.

Adaptation qualifies this conclusion. New target evidence can restore
performance, but only when the changed mechanism is represented in the chosen
features. Rank-state CUSUM success for sinkhole shows the value of generic
routing evidence matched to the changed mechanism.

Sybil is the clearest original extension because it changes the observable
surface from forwarding and rank behaviour to identity-related control-plane
behaviour. Its poor static transfer and strong adaptation response answer the
dissertation question directly.

The robustness campaign avoids an idealised conclusion. Attacker relocation and
radio loss caused false-positive-heavy static behaviour in several cases.
Adaptation recovered performance in tested Cooja scenarios, but this is not
proof of universal deployment robustness.

The defence result separates detection from mitigation. Sinkhole rank evidence
was useful for monitoring, yet direct parent avoidance caused churn and delivery
loss. Future work requires confidence aggregation, hysteresis, recovery, and
independently measured resource cost.

The Gope dataset is supporting work, not a direct replication of the Cooja
methodology. A live LLM explanation study is excluded from the core claim: it
would require fixed prompts and models, raw responses, and faithfulness scoring.
