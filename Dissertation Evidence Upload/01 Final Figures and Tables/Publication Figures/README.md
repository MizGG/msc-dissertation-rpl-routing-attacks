# Final Figures

These SVG figures were made from the completed result CSVs. They do not rerun Cooja or retrain any model.

- `cross_attack_cart_f1_heatmap.svg`: static CART transfer across the nine attack families.
- `online_drift_detection.svg`: held-out Sinkhole detection timing for CUSUM and delayed-label DDM.
- `robustness_static_vs_adapted_f1.svg`: static and adapted results under attacker relocation and lossy radio conditions.
- `sinkhole_defence_operational_cost.svg`: the negative result from the rank-based parent-selection prototype.
- `adaptation_f1_3d_surface.svg`: a 3D summary of mean held-out F1 by target family and adaptation budget.

The CSV tables contain the values used in the figures. To rebuild them:

```sh
python3 experiments/dissertation_final_figures_v2/build_final_figures.py
```
