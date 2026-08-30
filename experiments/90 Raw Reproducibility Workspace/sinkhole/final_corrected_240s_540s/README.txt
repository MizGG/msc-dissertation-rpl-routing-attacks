Sinkhole final corrected 240s/540s experiment set

Scope
- 16-mote RPL/UDP topology.
- 5 attack runs and 5 matched control runs.
- Seeds: 123456, 234567, 345678, 456789, 567890.
- Sinkhole activation delay: 240 seconds.
- Simulation timeout: 540 seconds.

Validation signal
- Attack runs log "SINKHOLE ATTACK: enabled" at approximately 04:00.
- Attack runs log exactly one immediate advertised-rank manipulation:
  "SINKHOLE: advertising rank 128 instead of 256".
- Control runs log "SINKHOLE CONTROL: started, normal RPL behaviour".
- All runs end with TEST OK.

Contents
- code/: source and Makefile snapshots used for this experiment.
- configs/: Cooja simulation configs for each seed and mode.
- runs/: raw Cooja outputs, including COOJA.testlog, COOJA.radio, and console.log.
- logs/: copied testlog and radio logs for quick browsing.
- validation_summary.csv: run-level validation counts.
- SHA256SUMS.txt: checksums for final experiment files.
