# Evidence Inventory

This inventory summarizes dissertation-related code and evidence recovered for
the first preservation commit. Classification key:

- A: Source code / implementation
- B: Earlier source version / backup
- C: Experiment configuration
- D: Reproducibility evidence
- E: Experimental result
- F: Generated build artefact
- G: Temporary / unimportant
- H: Uncertain - needs decision

## Top-Level Source And Build Files

| Path | Class | Purpose |
| --- | --- | --- |
| `Makefile` | A | Local Contiki-NG build configuration using RPL Lite. |
| `udp-client.c` | A | Baseline RPL/UDP client application. |
| `udp-server.c` | A | Baseline RPL DAG root and UDP server. |
| `control-router.c` | A | Control router with blackhole flag disabled. |
| `blackhole-router.c` | A | Final delayed blackhole router process. |
| `blackhole-node.c` | A/B | Earlier immediate blackhole node/client variant. |
| `dis-flooder.c` | A | DIS flooding attacker. |
| `silent-mote.c` | A | Silent control mote. |

## Earlier Source Versions And Backups

| Path | Class | Purpose |
| --- | --- | --- |
| `blackhole-router_before_240s_delay.c.backup` | B | Blackhole router before final 240-second timing. |
| `blackhole-router_before_shared_flag_fix.c` | B | Blackhole router before shared flag correction. |
| `blackhole-router_before_timing_fix.c.backup` | B | Blackhole router before timing correction. |
| `uip6_before_blackhole_logging_fix.c.backup` | B/D | Contiki IPv6 blackhole hook backup before logging fix. |
| `rpl-icmp6_before_sinkhole_hook.c.backup` | B/D | RPL ICMPv6 snapshot before sinkhole hook. |
| `BH_ATTACK_N16_SEED123456_before_timing_fix.csc.backup` | B/C | Attack configuration before timing fix. |
| `blackhole_forced_16_attack_before_positions.csc` | B/C | Earlier forced 16-mote attack configuration. |

## Cooja Configurations

| Path | Class | Purpose |
| --- | --- | --- |
| `rpl-udp-cooja.csc` | C | RPL/UDP Cooja example baseline. |
| `rpl-udp-sky.csc` | C | RPL/UDP Sky Cooja example baseline. |
| `baseline_rpl_udp_16_motes.csc` | C | 16-mote baseline RPL/UDP simulation. |
| `control silent 16 mote.csc` | C | Silent-control simulation for DIS flooding comparison. |
| `attack_dis_flood_16_motes.csc` | C | 16-mote DIS flooding attack simulation. |
| `attack_dis_flood_17_motes.csc` | C | 17-mote DIS flooding attack simulation. |
| `blackhole 16 mote.csc` | C | Earlier 16-mote blackhole/DIS configuration. |
| `blackhole debug 16 mote.csc` | C | Debug blackhole configuration. |
| `blackhole forced path 3 motes.csc` | C | Forced three-mote blackhole path experiment. |
| `blackhole final forced path 3 motes.csc` | C | Final forced three-mote blackhole path experiment. |
| `blackhole control forced path 3 motes.csc` | C | Forced three-mote control experiment. |
| `blackhole_forced_16_attack.csc` | C | Forced 16-mote blackhole attack. |
| `blackhole_forced_16_control.csc` | C | Forced 16-mote control. |
| `BH_ATTACK_N16_SEED*.csc` | C/D | Seeded final blackhole attack configurations. |
| `BH_CONTROL_N16_SEED*.csc` | C/D | Seeded final blackhole control configurations. |
| `experiments/blackhole/config_backups_before_headless/*.csc` | B/C | Configuration backups before headless runs. |
| `experiments/blackhole/config_backups_before_final_fix/*.csc` | B/C | Configuration backups before final correction. |
| `experiments/blackhole/final_corrected_240s_540s/configs/*.csc` | C/D | Final corrected experiment configurations. |

## Experiment Folders

| Path | Class | Purpose |
| --- | --- | --- |
| `experiments/blackhole/code/` | D/A | Source snapshots from blackhole experiment work. |
| `experiments/blackhole/logs/` | E | Blackhole experiment exported logs. |
| `experiments/blackhole/headless_runs/` | E | Raw headless Cooja outputs and console logs. |
| `experiments/blackhole/headless_test/` | E | Headless test output. |
| `experiments/blackhole/results/` | H | Empty or no files found during recovery scan. |
| `experiments/blackhole/configs/` | H | Empty or no files found during recovery scan. |
| `experiments/blackhole/final_corrected_240s_540s/` | D/E | Final corrected blackhole experiment evidence bundle. |

## Final Corrected Blackhole Evidence

| Path | Class | Purpose |
| --- | --- | --- |
| `experiments/blackhole/final_corrected_240s_540s/README.txt` | D | Final experiment description. |
| `experiments/blackhole/final_corrected_240s_540s/SHA256SUMS.txt` | D | Manifest for final experiment evidence. |
| `experiments/blackhole/final_corrected_240s_540s/validation_summary.csv` | E/D | Final validation summary. |
| `experiments/blackhole/final_corrected_240s_540s/code/` | D/A | Final source-code snapshots. |
| `experiments/blackhole/final_corrected_240s_540s/logs/` | E | Final exported mote and radio logs. |
| `experiments/blackhole/final_corrected_240s_540s/runs/` | E/D | Raw headless run outputs, radio logs, and console logs. |

## Logs And Result Evidence

| Path | Class | Purpose |
| --- | --- | --- |
| `experiment_notes.txt` | E/D | Narrative notes and measured DIS/blackhole outcomes. |
| `BH_VALIDATION_N16_SEED123456.log` | E | Blackhole validation log. |
| `BH_CONTROL_VALIDATION_N16_SEED123456.log` | E | Control validation log. |
| `D` | E/H | Unusually named file containing blackhole log evidence. |
| `experiments/blackhole/logs/*.log` | E | Earlier blackhole/control logs. |
| `experiments/blackhole/logs/*_radio.log` | E | Earlier radio logs. |
| `experiments/blackhole/headless_runs/*/COOJA.testlog` | E | Raw Cooja test logs. |
| `experiments/blackhole/headless_runs/*/COOJA.radio` | E | Raw Cooja radio logs. |
| `experiments/blackhole/headless_runs/*/console.log` | E | Headless run console logs. |
| `experiments/blackhole/final_corrected_240s_540s/runs/*/COOJA.testlog` | E/D | Final raw Cooja test logs. |
| `experiments/blackhole/final_corrected_240s_540s/runs/*/COOJA.radio` | E/D | Final raw Cooja radio logs. |
| `experiments/blackhole/final_corrected_240s_540s/runs/*/console.log` | E/D | Final headless console logs. |

## Archives

| Path | Class | Purpose |
| --- | --- | --- |
| `BH_FINAL_CORRECTED_N16_5SEEDS.zip` | D/E | Final corrected blackhole evidence archive. |
| `BH_COMPLETE_N16_5SEEDS.zip` | D/E | Earlier superseded blackhole evidence archive. |

## Contiki-NG Modifications Copied For Preservation

| Path | Class | Purpose |
| --- | --- | --- |
| `contiki-ng-modifications/CONTIKI_COMMIT.txt` | D | Source Contiki-NG commit hash at recovery time. |
| `contiki-ng-modifications/contiki-ng-dissertation-current.patch` | D | Current dissertation-related Contiki-NG diff. |
| `contiki-ng-modifications/current/os/net/ipv6/uip6.c` | A/D | Current Contiki IPv6 file with blackhole forwarding hook. |
| `contiki-ng-modifications/current/os/net/routing/rpl-lite/rpl-icmp6.c` | A/D | Current RPL ICMPv6 file with increase-rank and sinkhole hooks. |
| `contiki-ng-modifications/current/examples/rpl-udp/Makefile` | A/D | Current RPL UDP Makefile including blackhole targets. |
| `contiki-ng-modifications/history/examples/rpl-udp/blackhole-node.c` | A/B | Historical blackhole node from Contiki example folder. |
| `contiki-ng-modifications/history/examples/rpl-udp/blackhole-client.c` | A/B | Historical blackhole client from Contiki example folder. |
| `contiki-ng-modifications/history/examples/rpl-udp/Makefile.bak-before-blackhole-node` | B | Makefile before blackhole-node target addition. |
| `contiki-ng-modifications/history/os/net/ipv6/uip6.c.backup-before-blackhole` | B/D | Contiki IPv6 backup before blackhole hook. |
| `contiki-ng-modifications/history/os/net/ipv6/uip6.c.backup-before-blackhole-debug` | B/D | Contiki IPv6 backup before blackhole debug changes. |
| `contiki-ng-modifications/history/os/net/ipv6/uip6.c.bak` | B/D | Contiki IPv6 backup. |
| `contiki-ng-modifications/history/os/net/routing/rpl-lite/rpl-icmp6.c.before-increase-rank` | B/D | RPL ICMPv6 backup before increase-rank hook. |

## Generated Build Artefacts

| Path | Class | Purpose |
| --- | --- | --- |
| `build/cooja/*.cooja` | F | Generated Cooja binaries. |
| `build/cooja/obj/*.o` | F | Generated object files. |
| `build/cooja/obj/.deps/*.d` | F | Generated dependency files. |

These are retained for maximum preservation unless a later repository-size
decision excludes them.

## Temporary Or Low-Value Files

| Path | Class | Purpose |
| --- | --- | --- |
| `.DS_Store` | G | macOS metadata; ignored by preservation-first `.gitignore`. |

## Uncertain Items For Later Decision

| Path | Class | Reason |
| --- | --- | --- |
| `D` | H | Useful blackhole log evidence but has an unclear filename. |
| `rpl-udp.resc` | H/D | May be inherited test configuration; preserve unless confirmed unused. |
| `rpl-udp.robot` | H/D | May be inherited Robot/Renode test; preserve unless confirmed unused. |
| `build/` | H/F | Generated but may preserve local build state. |
