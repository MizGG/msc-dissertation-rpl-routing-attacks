# Sybil Attack

This is the Sybil extension to the RPL attack set. From 240 seconds, node 16 changes the IPv6 source address on outgoing RPL DIO messages. Neighbours therefore see rotating identities even though the mote and its RPL state remain the same.

This differs from the rank, forwarding and parent-selection attacks because it targets control-plane identity.

- `code/sybil-router.c` is the attacker.
- `code/sybil-control-router.c` is the matched normal-RPL control.
- `generate_configs.py` creates the Cooja configurations.
- `validate_runs.py` checks completion, activation and spoofed-DIO activity.
- `contiki_snapshots/uip-icmp6.c` records the Contiki hook used by the experiment.

Five attack and five control seeds were validated. Attack runs produced 150-151 spoofed identity events each; controls produced none. Marker fields were kept for validation but excluded from the IDS feature set.
