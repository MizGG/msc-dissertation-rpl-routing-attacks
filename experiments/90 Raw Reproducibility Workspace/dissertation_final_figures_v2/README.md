# Final Dissertation Figures v2

This package creates additional publication-ready SVG figures from completed
result CSVs. It performs no Cooja run, no model retraining, and no modification
of existing evidence.

## Figures

1. `cross_attack_cart_f1_heatmap.svg`: static CART transfer across all nine
   attack families. It should be used to support the controlled cross-attack
   distribution-shift argument, not a claim about naturally observed field
   drift.
2. `online_drift_detection.svg`: held-out sinkhole detection timing for CUSUM
   and delayed-label DDM.
3. `robustness_static_vs_adapted_f1.svg`: static and three-seed adapted results
   under attacker relocation and lossy radio conditions.
4. `sinkhole_defence_operational_cost.svg`: negative result showing the rank
   parent-selection prototype is operationally harmful in the tested topology.

The source tables mirror exactly the values drawn in the figures. Run:

```sh
python3 experiments/dissertation_final_figures_v2/build_final_figures.py
```

The script uses only Python standard-library modules.
