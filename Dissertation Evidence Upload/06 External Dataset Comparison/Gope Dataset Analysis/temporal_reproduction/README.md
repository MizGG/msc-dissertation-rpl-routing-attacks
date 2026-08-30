# Gope Temporal Reproduction

These tables use the supplied labelled attack CSVs. For each attack family, the first 70 percent of rows are used for training and the remaining 30 percent for testing. Six features are selected from the training part only.

This is a within-file temporal/order split. It is not a Cooja seed split and it is not a Blackhole-to-Sinkhole transfer test. It is included as external supporting evidence.

The selected fields include RPL-aware information such as source rank, parent, DIS count, DIO count, parent count and child count. That supports the routing-feature choice in the Cooja analysis.
