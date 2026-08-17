FINAL CORRECTED BLACKHOLE EXPERIMENT

Platform: Contiki-NG and Cooja
Network size: 16 motes
Root/server: mote 1
UDP clients: motes 2-15
Forwarding router: mote 16
Conditions: matched control and blackhole attack
Seeds: 123456, 234567, 345678, 456789, 567890
Simulation duration: 540 seconds

Experimental phases:
0-120 seconds: network convergence and warm-up
120-240 seconds: normal observation period
240-540 seconds: attack or matched control period

The attack router starts with packet dropping disabled.
Blackhole activation occurs at approximately 240 seconds.
The control router keeps packet forwarding enabled throughout.

Final validation:
All 10 runs completed with TEST OK.
All seeds matched their configuration.
No control run contained blackhole packet dropping.
No attack run dropped packets before activation.
Every attack run contained normal traffic before activation.
Every attack run contained packet drops after activation.

Files:
configs/ contains the ten final Cooja configurations.
code/ contains source-code snapshots.
logs/ contains the final exported mote and radio logs.
runs/ contains raw headless outputs and console records.
validation_summary.csv contains the final quality-control summary.

These corrected runs supersede the earlier 90-second blackhole batch.
