# Dissertation Project Handoff

## Authoritative Workspace

Use only:

`/Users/mizzy/Dissertation_Cooja_Work/rpl-dis-flood`

The copy under `/Users/mizzy/Documents/Dissertation/Dissertation_Cooja_Work/`
is a backup/reference copy. Do not edit it.

## Completed Scientific Work

The primary experiment is a controlled blackhole-to-sinkhole attack-distribution
shift in Contiki-NG/Cooja with five matched seeds, attack activation at 240 s and
simulation duration 540 s.

- Static routing-aware CART: recall 0.0000, F1 0.0000.
- Three-seed adaptation with coarse features: recall 0.0600, F1 0.0978.
- Three-seed adaptation with routing features: precision 1.0000, recall 0.9500,
  F1 0.9731, FPR 0.0000.
- Seed-separated rank-state CUSUM: detected 5/5 attacks in the first 240-300 s
  window, no pre-activation alarms and 0/5 control false alarms.
- Deterministic Gope blackhole-to-sinkhole baseline: accuracy 0.5083, recall
  0.0472, F1 0.0876.

Primary result text:

`experiments/results/DISSERTATION_RESULTS_SO_FAR.md`

Primary routing evidence:

`experiments/routing_features_v1/`

## LLM Explanation Work

`scripts/build_llm_explanation_package.py` creates five label-free explanation
requests and hidden evaluation cases under `experiments/llm_explanations/`.
The package uses IDS metrics, persistent non-root rank state and CUSUM evidence.
It prohibits unsupported claims about node identity, packet dropping or proven
attack identity.

The secure OpenAI API-key picker was opened but did not complete. No key was
saved in the environment, `.env` or `.env.local`, and no live model request was
made. The next chat should either finish secure key setup or evaluate the saved
requests with an explicitly selected available model. Never print or commit a
plaintext key.

## Git State

Local commits after the remote checkpoint:

- `ede191c` routing-aware sinkhole adaptation experiment;
- `4edb611` seed-separated routing drift monitor;
- `373481f` deterministic Gope external validation.
- the latest `Add offline LLM explanation evaluation package` commit; use
  `git log -1 --oneline` to obtain its hash.

GitHub `main` was successfully advanced through `4f80d09`. Pushing later commits
over HTTPS returned HTTP 400. GitHub recognised the local SSH public key but SSH
signature authentication still failed. The user asked to pause that issue.

Do not stage existing generated/unverified artefacts:

- `build/cooja/obj/*.o` modifications;
- `experiments/routing_features_v1/code/build/`;
- `experiments/sinkhole/runs/`;
- `experiments/sinkhole/validation_summary.csv`.

## Immediate Next Actions

1. Re-run `scripts/build_llm_explanation_package.py` if upstream evidence changes.
2. After secure API access is available, run one fixed model/configuration over
   all five requests and preserve raw JSON outputs.
3. Score outputs with `scripts/score_llm_explanations.py`; report mean score,
   unsupported-claim rate and JSON-validity rate.
4. Add the explanation results to the dissertation results and limitations.

Do not implement more Cooja attacks unless the supervisor explicitly requires a
new attack surface. Concept drift, routing-aware adaptation, formal monitoring
and external validation are already implemented.
