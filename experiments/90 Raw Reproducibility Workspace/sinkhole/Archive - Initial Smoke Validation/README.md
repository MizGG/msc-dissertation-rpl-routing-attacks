# Sinkhole Experiment

This folder contains the initial sinkhole attack implementation and one
matched 16-mote Cooja smoke validation pair.

## Layout

- `code/`: sinkhole application sources, Makefile snapshot, implementation
  notes, and the `rpl-icmp6.c` snapshot containing the shared-flag hook.
- `configs/`: seed-123456 attack and control Cooja configurations.
- `runs/`: generated `COOJA.testlog` and `COOJA.radio` output for the smoke
  validation pair.
- `validation_summary.csv`: compact result summary.

## Validation Signal

The attack run starts with normal RPL behaviour, enables the sinkhole at
`04:00.473`, and immediately advertises a manipulated rank:

```text
04:00.473 ID:16 [WARN: RPL] SINKHOLE: advertising rank 128 instead of 256
```

The control run keeps `sinkhole_attack_enabled` at `0` and has no advertised
rank manipulation events. Both smoke runs completed the 540-second simulation
with `TEST OK`.
