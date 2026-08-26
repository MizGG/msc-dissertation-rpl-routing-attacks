# Core Dissertation Argument

## Main Claim

The IDS generalises poorly under cross-attack concept drift. Whole-seed
adaptation improves performance, especially for Sybil and several routing
attacks, but failures show that retraining alone is not enough when the feature
representation does not expose the changed attack mechanism.

## Evidence Chain

1. The Cooja campaign validates nine RPL attack families with matched attack
   and control runs: blackhole, sinkhole, DIS flood, grayhole, increase-rank,
   DIO suppression, worst-parent, wormhole and Sybil.
2. The static cross-attack experiment trains on one attack family and tests on
   another, creating a controlled attack-distribution change.
3. Static CART models produce 48 zero-recall failures across 72 cross-attack
   pairs, showing that many changed attack environments are missed entirely.
4. Whole-seed adaptation improves mean CART F1 from 0.1822 with no target seeds
   to 0.8258 with one target seed, 0.8664 with two and 0.8792 with three.
5. Sybil provides the strongest new attack-surface result: static Sybil-target
   F1 is 0.2183, while one whole Sybil adaptation seed raises held-out F1 to
   0.9683.
6. The trust-layer result is deliberately cautious. It improves
   interpretability but does not improve CART metrics, showing that robustness
   depends on measuring the right attack mechanism rather than simply adding a
   new abstraction.
7. The external Gope/professor dataset supports baseline credibility by showing
   that the IDS pipeline can reproduce strong supervised classification on
   existing 6LoWPAN/RPL data, while the Cooja experiments provide the controlled
   drift, adaptation and Sybil contribution.

## Defensible Wording

Use:

> This study evaluates controlled attack-distribution drift in RPL/6LoWPAN IDS
> by training on one attack family and testing on another. The results show that
> static models often fail to detect changed attack behaviour, while limited
> whole-run target adaptation can substantially recover performance. However,
> adaptation is only effective when the feature representation exposes the new
> attack mechanism.

Avoid:

> The IDS solves concept drift.

Avoid:

> The trust layer prevents the attacks.

Avoid:

> The LLM detects attacks.

## Viva Answer

If asked what the original contribution is, answer:

> I reproduced and extended a Cooja/RPL attack evaluation into a controlled
> concept-drift study. The key contribution is not only implementing more
> attacks; it is showing that IDS models trained on one RPL attack mechanism
> often fail under another, then quantifying how whole-seed adaptation recovers
> performance. I also added Sybil as a new identity-manipulation attack surface
> and used trust and LLM layers as interpretability tools rather than claiming
> them as complete defences.
