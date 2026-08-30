# Sybil Rate Variants

These are isolated Cooja applications for testing Sybil attack intensity. They use the existing Sybil hook without changing it.

- `sybil-low-rate-router.c`: one spoofed DIO every 10 seconds after 240 seconds.
- `sybil-high-rate-router.c`: one spoofed DIO every second after 240 seconds.
- `sybil-rate-control-router.c`: normal-RPL control.

Five attack seeds were run for each rate, with five shared controls. `project-conf.h` makes the virtual source address visible in the Cooja log; it does not change routing behaviour.

```sh
make sybil-low-rate-router.cooja TARGET=cooja
make sybil-high-rate-router.cooja TARGET=cooja
make sybil-rate-control-router.cooja TARGET=cooja
```
