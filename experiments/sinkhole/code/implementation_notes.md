# Sinkhole Milestone 1 Implementation Notes

## Shared flag

The sinkhole application uses the shared weak flag declared in Contiki-NG's
RPL-Lite ICMPv6 code:

```c
extern int sinkhole_attack_enabled;
```

Normal firmware leaves the weak flag disabled. The sinkhole application sets it
to `0` at startup, then later sets it to `1`. The sinkhole control application
sets the same flag to `0` at startup and never enables it.

## Activation timing

`sinkhole-router.c` starts with normal RPL behaviour and waits:

```c
#define ATTACK_START_DELAY (240 * CLOCK_SECOND)
```

After the 240-second convergence period, it sets
`sinkhole_attack_enabled = 1` and logs:

```text
SINKHOLE ATTACK: enabled
```

The attack application then resets the RPL-Lite DIO Trickle timer with
`rpl_timers_dio_reset("Sinkhole attack enabled")` and sends one multicast DIO
with `rpl_icmp6_dio_output(NULL)`. This makes the manipulated rank visible
immediately after activation, while subsequent DIOs continue under normal RPL
timer control.

## Advertised-rank manipulation

The Contiki-NG hook in `rpl-icmp6.c` only changes the rank placed in outgoing
DIO messages. When `sinkhole_attack_enabled` is active and the node is not in
leaf-only mode, the advertised rank is set to `RPL_MIN_HOPRANKINC`.

The node's real internal DAG rank remains unchanged, so the manipulation is
limited to the DIO rank field used by neighbouring nodes for parent selection.
