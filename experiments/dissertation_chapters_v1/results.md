# Results

## Attack Validation

Nine attack families were validated in Cooja. Each family has five attack runs
and five matched control runs. All 90 runs completed validation.

The attack coverage table is stored in
`experiments/dissertation_results_summary_v1/attack_coverage_table.csv`.

The validated families are blackhole, sinkhole, DIS flood, grayhole,
increase-rank, DIO suppression, worst-parent, wormhole and Sybil. Sybil is the
new attack-surface contribution.

## Static Cross-Attack Drift

The nine-family static cross-attack experiment shows poor generalisation when a
model trained on one attack family is tested on another. For the CART model,
there are 72 cross-attack train/test pairs. Of these, 48 have zero attack recall
and only 6 reach F1 >= 0.8.

The Gaussian model performs worse in this setting: 66 of 72 cross-attack pairs
have zero recall and no pair reaches F1 >= 0.8.

This supports the claim that static IDS performance is brittle under
attack-distribution change.

## Adaptation

The adaptation experiment shows that adding limited target-family data improves
performance. With no target adaptation seeds, mean CART recall is 0.2333 and
mean F1 is 0.1822. With one whole target seed, mean recall increases to 0.8056
and mean F1 to 0.8258. With two target seeds, mean F1 reaches 0.8664. With three
target seeds, mean F1 reaches 0.8792.

The adaptation result supports the claim that static model failure under drift
can be partially recovered when representative examples from the new
environment are introduced.

## Sybil Attack Surface

Sybil strengthens the dissertation contribution because it changes the attack
surface. It does not primarily drop packets or manipulate rank. Instead, it
causes neighbouring nodes to observe RPL DIO control messages from rotating
virtual identities.

Static CART models involving Sybil show 11 zero-recall failures out of 16
Sybil-related cross-attack pairs. When Sybil is the target family, mean F1 is
0.2183 with no Sybil adaptation data. With one Sybil adaptation seed, mean F1
increases to 0.9683.

This is a strong example of concept drift: a new attack mechanism is poorly
handled by static models trained on older attack surfaces, but limited
adaptation restores performance.

## Trust Layer

The offline trust layer did not improve CART cross-attack IDS metrics over the
existing routing-feature baseline. Static CART F1 remains 0.1822, and adaptation
F1 values remain unchanged.

This is a useful negative result. The trust scores are transformations of
signals already available in the routing-window feature set, so they improve
interpretability more than predictive power.

The trust alerts are still informative. Blackhole and grayhole mainly affect
forwarding trust. Sinkhole affects rank trust. DIS flood and Sybil affect
control-message trust. Worst-parent affects control and route trust. Wormhole is
weakly covered by this simple trust design.

## LLM Explanation Layer

The LLM v2 package creates one structured explanation case per attack family.
Each case contains model context, adaptation context, attack-vs-control feature
deltas, trust alerts and top changed features. Hidden labels and simulator
attack markers are excluded from model-facing prompts.

The scoring pipeline was validated using handcrafted and deterministic
fixtures. This confirms that the JSON schema, evidence packaging and scorer
work, but these fixtures are not external live model performance. A final live
LLM evaluation should preserve raw responses, model identifier, prompt settings
and scores.
