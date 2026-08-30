# Prepared Cooja Sybil Rate Variants

These are new, isolated Cooja applications. They reuse the already validated
weak `sybil_attack_enabled` hook but do not change it.

- `sybil-low-rate-router.c`: spoofed RPL DIO every 10 seconds after 240 s;
- `sybil-high-rate-router.c`: spoofed RPL DIO every 1 second after 240 s;
- `sybil-rate-control-router.c`: matching normal-RPL control.

The configuration generator creates five attack and five control configurations
for each rate. The applications were compiled for `TARGET=cooja`; the checked-in
campaign has validated five seeds for each attack rate and five shared controls.
The raw logs are in `../runs/` and the validator output is in
`../results/sybil_rate_campaign_validation.csv`.

`project-conf.h` enables IPv6 warning logs only for these applications. It
makes the virtual IPv6 source identity emitted by the pre-existing Sybil hook
observable in Cooja logs; it does not modify the hook or routing behaviour.

Build from this directory:

```bash
make sybil-low-rate-router.cooja TARGET=cooja
make sybil-high-rate-router.cooja TARGET=cooja
make sybil-rate-control-router.cooja TARGET=cooja
```
