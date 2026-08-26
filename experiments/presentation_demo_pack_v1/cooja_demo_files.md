# Cooja Demo Files

Use Cooja to show one or two simulations only. Do not run full batches live.

## Best Primary Demo

Sybil attack:

`/Users/mizzy/Dissertation_Cooja_Work/rpl-dis-flood/experiments/sybil_attack_v1/configs/SYBIL_ATTACK_N16_SEED123456.csc`

Why this is good:

- It is the new attack surface.
- It has clear log evidence.
- It supports the originality/contribution part of the dissertation.

Evidence to show:

`/Users/mizzy/Dissertation_Cooja_Work/rpl-dis-flood/experiments/sybil_attack_v1/validation_summary.csv`

Look for:

- `SYBIL ATTACK: enabled`
- `SYBIL: sending RPL DIO as virtual identity`

## Backup Cooja Files

Blackhole:

`/Users/mizzy/Dissertation_Cooja_Work/rpl-dis-flood/experiments/blackhole/final_corrected_240s_540s/configs/BH_ATTACK_N16_SEED123456.csc`

Sinkhole:

`/Users/mizzy/Dissertation_Cooja_Work/rpl-dis-flood/experiments/sinkhole/final_corrected_240s_540s/configs/SH_ATTACK_N16_SEED123456.csc`

DIS flood:

`/Users/mizzy/Dissertation_Cooja_Work/rpl-dis-flood/experiments/additional_attacks_v1/configs/DIS_FLOOD_ATTACK_N16_SEED123456.csc`

Wormhole:

`/Users/mizzy/Dissertation_Cooja_Work/rpl-dis-flood/experiments/additional_attacks_v1/configs/WORMHOLE_ATTACK_N17_SEED123456.csc`

## Recording Plan

Record short clips in advance:

- Sybil: virtual identity DIO messages after 240 seconds.
- Blackhole: attack activation and forwarding-drop evidence.
- Sinkhole: advertised-rank manipulation after 240 seconds.
- Control: a matched control run with no attack marker.

Each clip only needs to be 20-40 seconds. The point is to prove you can show
the simulation if live Cooja behaves slowly.

