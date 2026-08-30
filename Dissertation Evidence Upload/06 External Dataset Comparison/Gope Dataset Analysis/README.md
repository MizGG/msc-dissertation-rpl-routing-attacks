# Gope Dataset Audit

This folder audits the eight supplied Dr Gope 6LoWPAN/RPL CSV files before reproducing a static baseline. It records row counts, labels, missing values and shared columns.

Seven of the eight files have a `TYPE` label. Forty-three columns are common to every file.

- `audit_summary.csv` records the file-level checks.
- `column_overlap.csv` lists shared fields.
- `missing_values.csv` records missing values where present.

Use this material as an external comparison with the Cooja work, not as a replacement for the seed-separated Cooja experiment.
