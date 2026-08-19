# Supplied Gope Dataset Audit

Dataset source: `/Users/mizzy/Documents/Dissertation/Dissertation_Cooja_Work/DR P`

This audit covers the supplied Dr Gope 6LoWPAN/RPL CSV files before baseline reproduction. It records row counts, schema size, TYPE label availability, label counts, missing values and column overlap.

CSV files audited: 8

Files with `TYPE` labels: 7 / 8

Columns common to all files: 43

Outputs:

- `audit_summary.csv`
- `column_overlap.csv`
- `missing_values.csv` when missing values are present

Use this audit before reproducing the paper baseline or mapping the supplied data to independently generated Cooja features.
