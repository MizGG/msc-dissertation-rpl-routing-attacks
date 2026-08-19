# Routing-Aware Cooja Milestone

This package reuses the validated 16-node blackhole and sinkhole topologies, five seeds, 240-second activation and 540-second duration. It does not modify the preserved final evidence packages.

The only simulation-setting change is `LOG_CONF_LEVEL_RPL=LOG_LEVEL_INFO`, which exposes Contiki-NG's generic DIO rank, parent-switch, DIS and DAO logs. The sinkhole router firmware also provides a strong flag definition to prevent Cooja shared-library weak-symbol interposition; the RPL hook remains unchanged. Explicit attack markers are retained for validation but excluded from IDS features.
