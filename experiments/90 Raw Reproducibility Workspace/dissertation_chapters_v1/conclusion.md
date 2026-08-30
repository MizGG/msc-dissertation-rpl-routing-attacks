# Conclusion

This project implemented and evaluated an RPL/6LoWPAN IDS workflow under
controlled attack-distribution change. Nine attack families were validated in
Contiki-NG/Cooja, producing 90 validated simulation runs. The work reproduced
multiple established RPL attack behaviours and added Sybil identity
manipulation as a new attack surface.

The main finding is that static IDS models are brittle under cross-attack
concept drift. When trained on one attack family and tested on another, the CART
model produced zero attack recall in 48 of 72 cross-attack pairs. This shows
that strong performance in one attack environment does not guarantee
generalisation to a changed attack mechanism.

The adaptation experiment showed that limited target-environment data can
restore detection performance. Mean CART F1 improved from 0.1822 with no target
adaptation seeds to 0.8258 with one whole target seed and 0.8792 with three
target seeds. This supports the value of adaptation under evolving attack
behaviour.

The Sybil experiment strengthened the contribution by introducing identity
manipulation into the RPL control plane. Static models often failed on Sybil,
while limited Sybil adaptation restored high held-out performance. This connects
the new attack surface directly to the concept-drift question.

The trust layer provided useful diagnostic interpretation but did not improve
IDS metrics over the existing routing features. This is a defensible negative
result: trust scores derived from existing features improve explanation more
than predictive power unless they introduce genuinely new evidence or affect
routing decisions online.

The LLM layer was packaged as an evidence-grounded explanation component. It
does not detect attacks. Instead, it converts IDS, drift, adaptation and trust
evidence into structured explanations that can be evaluated for faithfulness,
uncertainty and unsupported claims.

Overall, the dissertation demonstrates that IDS evaluation for RPL networks
should consider not only attack detection in a static setting, but also
generalisation under changing attack behaviour, recovery through adaptation and
the explainability of model decisions under drift.

