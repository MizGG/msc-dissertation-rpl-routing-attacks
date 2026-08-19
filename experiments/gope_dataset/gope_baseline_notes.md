# Preliminary Gope Baseline

This is a first reproducible supervised baseline over the seven labelled 71-column supplied datasets. Worst Parent is excluded because the audit found no `TYPE` label.

The model uses a simple Gaussian baseline over routing-aware features such as rank, parent count, DIO/DAO/DIS counts, hop count and packet loss. Rows are class-balanced per attack family before training.

Important limitation: the supplied CSVs do not currently expose run IDs, so this is not yet a run-separated reproduction. Treat it as the first baseline audit result, not the final paper reproduction.
