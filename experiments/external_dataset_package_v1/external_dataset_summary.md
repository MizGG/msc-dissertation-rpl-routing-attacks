# External Dataset Package

This package connects the supplied Gope/professor dataset work to the main
Cooja dissertation experiments.

The word "connect" here does not mean merging the datasets. It means explaining
how each evidence source supports a different part of the dissertation.

## External Dataset Role

The supplied external dataset is used to validate the baseline IDS pipeline
against existing 6LoWPAN/RPL-style attack data. The reproduced static baseline
uses eight attack datasets and evaluates simple supervised models under random
and temporal/source-order splits.

The strongest conservative baseline is the temporal/source-order Random Forest
top-six result:

- mean accuracy: 99.63%;
- mean recall: 98.57%;
- mean F1: 98.08%;
- mean FPR: 0.0043.

This shows that the IDS pipeline can learn known attack patterns in an external
dataset setting.

## Cooja Role

The Cooja experiments provide the main original experimental contribution:

- nine validated attack families;
- 90 validated Cooja runs;
- whole-seed static cross-attack drift;
- whole-seed adaptation curves;
- Sybil as a new RPL identity-manipulation attack surface;
- trust and LLM explanation layers built from Cooja evidence.

## Main Combined Argument

The combined dissertation argument is:

1. The external dataset validates the baseline IDS workflow against prior
   6LoWPAN/RPL attack data.
2. The Cooja simulations provide controlled attack evolution, allowing concept
   drift and adaptation to be evaluated cleanly.
3. The Sybil experiment adds a new attack surface beyond the reproduced attack
   families.
4. The LLM layer explains IDS/drift/trust evidence; it does not perform attack
   detection directly.

## Evidence Files

- External baseline summary: `gope_baseline_results.csv`
- Per-family temporal results: `gope_temporal_family_results.csv`
- Scope comparison: `cooja_vs_external_scope_table.csv`
- Dissertation wording guide: `how_external_dataset_supports_dissertation.md`

Original baseline reproduction files are preserved in:

`experiments/gope_dataset/paper_baseline_reproduction`

