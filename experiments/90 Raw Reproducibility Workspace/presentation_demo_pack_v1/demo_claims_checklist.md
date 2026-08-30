# Demo Claims Checklist

Use these claims.

## Safe Claims

- I implemented and validated nine RPL attack families in Cooja.
- Each attack family has five attack and five matched control runs.
- The main validated Cooja set contains 90 runs.
- Static IDS models often fail when trained on one attack family and tested on
  another.
- Whole-seed adaptation improves performance after attack-distribution change.
- Sybil is my new attack-surface contribution.
- The trust layer is an offline diagnostic/explanation layer.
- The LLM explains structured IDS/drift/trust evidence; it is not the detector.
- The external Gope/professor dataset supports baseline IDS credibility.

## Avoid These Claims

- Do not say the LLM detects attacks.
- Do not say the trust layer prevents all attacks.
- Do not say Sybil exists in the professor dataset.
- Do not say the external dataset proves the Cooja drift result.
- Do not say Cooja proves real-world deployment performance.
- Do not report deterministic LLM fixture scores as live model performance.

## Short Defence If Challenged

If asked why not run all Cooja simulations live:

The full simulation campaign is preserved and validated. A live presentation
should demonstrate representative evidence and reproducible analysis commands,
not spend several minutes rerunning all simulation seeds.

