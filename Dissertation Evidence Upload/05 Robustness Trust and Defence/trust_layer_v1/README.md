# Trust Layer

This is an offline trust-feature experiment using the existing Cooja logs. It does not change RPL parent selection.

The features are forwarding trust, rank trust, control-message trust and route trust. They are combined as `trust_total` using weights of 0.40, 0.25, 0.20 and 0.15.

The trust features help explain different attack mechanisms: forwarding loss for Blackhole and Grayhole, rank anomalies for Sinkhole, control activity for DIS flood and Sybil, and route instability for Worst Parent.

They did not improve the current CART cross-attack results beyond the routing-feature baseline. The useful contribution is diagnostic interpretation rather than a demonstrated routing defence.
