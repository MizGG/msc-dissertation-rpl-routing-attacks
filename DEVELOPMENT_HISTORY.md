# Development History

Git version control for this dissertation recovery repository was introduced on
17 August 2026. The first preservation commit is `2a655c3`:

`Initial dissertation preservation: recovered development history and experiment evidence`

The files in this repository were not created by a historical Git timeline.
Files labelled as backups, earlier versions, or `before` variants are recovered
development artefacts created before Git tracking began.

This repository is therefore intended to preserve the MSc dissertation
development record honestly: the first Git commit records the recovered state
as it existed on 17 August 2026, not fabricated earlier commit dates or a
pretence that Git was used during the original experimentation.

Many files in commit `2a655c3` were created or modified before Git tracking
began. Their surviving filesystem modification timestamps, experiment
timestamps, backup filenames, source snapshots, SHA256 manifests, and archive
contents are preserved as historical development evidence. The Git commit date
must not be interpreted as the date every contained file was originally
developed.

Filesystem timestamp evidence recovered after the first preservation commit is
listed in:

- `HISTORICAL_FILE_TIMESTAMPS.csv`

## Preservation Policy

The following filename patterns are intentionally retained as historical
development evidence:

- `*.bak`
- `*.backup`
- `*_before_*`
- `*.before-*`
- copied Contiki-NG source snapshots and patches
- old Cooja configurations, logs, runs, and archives

These files may include superseded or intermediate work. They should not be
deleted merely because a later final experiment exists.

## Earliest Surviving Evidence Dates

The following dates come from filesystem modification timestamps that survived
on disk at recovery time. They are evidence, not a complete authorship timeline.

| Area | Earliest surviving timestamp | Evidence path |
| --- | --- | --- |
| Baseline RPL/UDP | 2026-06-25 14:35:24 +0100 | `experiments/blackhole/final_corrected_240s_540s/code/udp-client.c`, `experiments/blackhole/final_corrected_240s_540s/code/udp-server.c` |
| Baseline RPL/UDP configuration | 2026-07-02 14:14:00 +0100 | `rpl-udp-cooja.csc`, `rpl-udp-sky.csc`, `README.md` |
| DIS flooding | 2026-07-02 14:20:18 +0100 | `dis-flooder.c` |
| DIS flooding control | 2026-07-02 16:19:32 +0100 | `silent-mote.c` |
| Blackhole stack hook evidence | 2026-07-02 16:52:02 +0100 | `contiki-ng-modifications/history/os/net/ipv6/uip6.c.backup-before-blackhole` |
| Blackhole application evidence | 2026-07-02 16:53:30 +0100 | `blackhole-node.c` |
| Blackhole Cooja experiment evidence | 2026-07-05 12:54:58 +0100 | `blackhole 16 mote.csc` |
| Increase-rank development | 2026-07-27 16:16:56 +0100 | `contiki-ng-modifications/history/os/net/routing/rpl-lite/rpl-icmp6.c.before-increase-rank` |
| Increase-rank snapshot / pre-sinkhole RPL file | 2026-07-27 16:26:55 +0100 | `rpl-icmp6_before_sinkhole_hook.c.backup`, `experiments/blackhole/final_corrected_240s_540s/code/rpl-icmp6_snapshot.c` |
| Blackhole timing/shared flag fixes | 2026-08-12 12:32:18 +0100 | `blackhole-router_before_shared_flag_fix.c`, `blackhole-router_before_timing_fix.c.backup` |
| Final blackhole corrected code | 2026-08-17 13:12:04 +0100 | `blackhole-router.c`, `experiments/blackhole/final_corrected_240s_540s/code/blackhole-router.c` |
| Final blackhole corrected configurations | 2026-08-17 13:20:22 +0100 | `BH_ATTACK_N16_SEED*.csc`, `BH_CONTROL_N16_SEED*.csc` |
| Final blackhole corrected logs | 2026-08-17 13:21:49 +0100 | `experiments/blackhole/final_corrected_240s_540s/logs/` and `runs/` |
| Final blackhole manifest/archive | 2026-08-17 13:27:10 +0100 / 2026-08-17 13:27:11 +0100 | `SHA256SUMS.txt`, `BH_FINAL_CORRECTED_N16_5SEEDS.zip` |
| Sinkhole development | 2026-08-17 14:05:55 +0100 | `contiki-ng-modifications/current/os/net/routing/rpl-lite/rpl-icmp6.c` |

## Baseline RPL/UDP

The project contains baseline RPL/UDP application code and configurations:

- `udp-server.c` starts the RPL DAG root and echoes UDP payloads.
- `udp-client.c` sends periodic UDP requests to the DAG root and records
  transmit/receive counters.
- `baseline_rpl_udp_16_motes.csc`, `rpl-udp-cooja.csc`, and `rpl-udp-sky.csc`
  preserve baseline Cooja configurations.
- `Makefile` records the local Contiki-NG path and RPL Lite routing build
  configuration.

## DIS Flooding

The DIS flooding attack implementation is preserved in `dis-flooder.c`. It
periodically sends multicast DIS messages via `rpl_icmp6_dis_output(NULL)`.

Related configurations and evidence include:

- `attack_dis_flood_16_motes.csc`
- `attack_dis_flood_17_motes.csc`
- `control silent 16 mote.csc`
- `silent-mote.c`
- `experiment_notes.txt`

The notes record observed radio-packet comparisons between normal/control
simulations and DIS flooding simulations.

## Blackhole Development

Several blackhole implementations and experiments are preserved:

- `blackhole-node.c` records an earlier immediate blackhole behaviour in a
  UDP-client-style mote.
- `blackhole-router.c` records the later router-specific blackhole process.
- `blackhole forced path 3 motes.csc`, `blackhole final forced path 3 motes.csc`,
  and `blackhole control forced path 3 motes.csc` preserve forced-path
  three-mote experiments.
- `blackhole 16 mote.csc`, `blackhole debug 16 mote.csc`,
  `blackhole_forced_16_attack.csc`, and `blackhole_forced_16_control.csc`
  preserve larger blackhole experiment variants.

The Contiki-NG IPv6 forwarding hook is preserved in:

- `contiki-ng-modifications/current/os/net/ipv6/uip6.c`
- `experiments/blackhole/code/uip6_blackhole_modified.c`
- `experiments/blackhole/final_corrected_240s_540s/code/uip6_blackhole_modified.c`

## Blackhole Timing And Shared Flag Fixes

Recovered files show intermediate blackhole development and corrections:

- `blackhole-router_before_240s_delay.c.backup`
- `blackhole-router_before_shared_flag_fix.c`
- `blackhole-router_before_timing_fix.c.backup`
- `uip6_before_blackhole_logging_fix.c.backup`
- `BH_ATTACK_N16_SEED123456_before_timing_fix.csc.backup`
- `experiments/blackhole/config_backups_before_headless/`
- `experiments/blackhole/config_backups_before_final_fix/`

These files are intentionally retained to document the debugging and timing
history, including the transition to the final 240-second attack activation.

## Final Blackhole Experiment

The final corrected blackhole experiment is preserved under:

- `experiments/blackhole/final_corrected_240s_540s/`
- `BH_FINAL_CORRECTED_N16_5SEEDS.zip`

Its README states the experiment used 16 motes, five seeds, 540-second
simulations, and a 240-second blackhole activation point. The folder also
contains:

- final Cooja configurations in `configs/`
- source snapshots in `code/`
- final exported logs in `logs/`
- raw headless outputs in `runs/`
- `validation_summary.csv`
- `SHA256SUMS.txt`

The earlier archive `BH_COMPLETE_N16_5SEEDS.zip` is retained as historical
evidence of a superseded blackhole batch.

## Increase-Rank Attack

Increase-rank attack code is preserved in the modified Contiki-NG RPL ICMPv6
file:

- `contiki-ng-modifications/current/os/net/routing/rpl-lite/rpl-icmp6.c`

Historical and snapshot evidence includes:

- `rpl-icmp6_before_sinkhole_hook.c.backup`
- `contiki-ng-modifications/history/os/net/routing/rpl-lite/rpl-icmp6.c.before-increase-rank`
- `experiments/blackhole/final_corrected_240s_540s/code/rpl-icmp6_snapshot.c`

The current implementation includes a weak `increase_rank_attack_enabled` flag
and DIO rank-advertisement logic.

## Sinkhole Development

Sinkhole development is preserved in the current copied Contiki-NG RPL ICMPv6
file:

- `contiki-ng-modifications/current/os/net/routing/rpl-lite/rpl-icmp6.c`

The current hook introduces `sinkhole_attack_enabled` and advertises
`RPL_MIN_HOPRANKINC` in outgoing DIO messages while preserving the node's
internal RPL rank. At the time of recovery, no application-side source file in
this dissertation folder was found setting `sinkhole_attack_enabled = 1`.

## Control And Baseline Simulations

Control and baseline evidence is preserved through:

- `control-router.c`
- `silent-mote.c`
- `BH_CONTROL_N16_SEED*.csc`
- `experiments/blackhole/final_corrected_240s_540s/configs/BH_CONTROL_N16_SEED*.csc`
- `experiments/blackhole/final_corrected_240s_540s/logs/BH_CONTROL_N16_SEED*.log`
- `experiments/blackhole/final_corrected_240s_540s/runs/BH_CONTROL_N16_SEED*/`

These files document matched control conditions for the final blackhole
experiment and earlier baseline/control simulation work.

## Contiki-NG Recovery Copies

The live Contiki-NG repository is not modified by this recovery process. Current
and historical dissertation-related Contiki files are copied into
`contiki-ng-modifications/` so the dissertation repository can preserve the
modified network stack code reproducibly.

The source Contiki-NG commit hash is recorded in:

- `contiki-ng-modifications/CONTIKI_COMMIT.txt`

The current dissertation-related Contiki diff is recorded in:

- `contiki-ng-modifications/contiki-ng-dissertation-current.patch`
