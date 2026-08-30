# Cross-Attack Drift With Sybil

This extends the cross-attack matrix to nine families: Blackhole, Sinkhole, DIS flood, Grayhole, Increase Rank, DIO suppression, Worst Parent, Wormhole and Sybil.

The IDS uses routing-window features. Simulator markers, including attack-enabled and Sybil spoofing fields, were not used as model features.

Results: 72 static CART transfer pairs were tested. Forty-eight had zero attack recall and only six reached F1 of at least 0.8. Of the 16 Sybil-related pairs, 11 had zero recall and three reached F1 of at least 0.8.

The result shows that a model trained on one RPL attack often does not recognise a different attack mechanism.
