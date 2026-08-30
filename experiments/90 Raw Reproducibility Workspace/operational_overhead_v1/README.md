# Operational Overhead Evidence v1

This folder derives a compact operational-overhead table from the completed
five-seed sinkhole-defence Cooja campaign in
`experiments/sinkhole_defence_v1/`.

Run `python3 build_overhead_table.py` from the repository root to recreate
`operational_overhead_table.csv`.

The table reports post-activation application responses, missed responses,
parent switches, and Cooja radio transmission events. Radio transmissions are
an activity proxy only; they are not an energy measurement.

No binary ROM/RAM metric is reported. The campaign uses the Cooja native target,
whose `.cooja` files are host shared libraries rather than firmware images for
an embedded mote. Treating their macOS file size as mote code size would be
misleading.
