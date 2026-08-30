# Sybil Attack Workstream

This package implements a new RPL control-plane attack surface separate from
the professor-paper attack-family reproduction package.

The Sybil attacker keeps the real mote and RPL state intact, but after 240
seconds it spoofs the IPv6 source address of outgoing RPL DIO messages so that
neighbouring motes observe control messages from rotating virtual identities.

This is intentionally different from sinkhole, increase-rank and worst-parent:
the manipulated surface is identity, not advertised rank, forwarding behaviour
or parent selection.

## Files

- `code/sybil-router.c`: delayed attacker, initially disabled.
- `code/sybil-control-router.c`: matched control, permanently disabled.
- `generate_configs.py`: creates five attack and five control Cooja configs.
- `validate_runs.py`: validates Cooja completion, activation and spoofed DIO
  evidence.
- `contiki_snapshots/uip-icmp6.c`: snapshot of the live Contiki Sybil hook.

## Status

Validated with five attack and five matched control Cooja seeds. Attack runs
activate once at 240 seconds and produce 150-151 spoofed DIO identity events
per run; controls produce zero Sybil activation/spoofing markers.

These marker fields are retained in extracted CSVs for validation and
diagnosis, but excluded from the primary cross-attack IDS feature set to avoid
simulator-log leakage.
