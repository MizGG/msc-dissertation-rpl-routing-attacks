# Presentation Demo Pack V1

This folder is the practical presentation/demo guide.

Use three apps:

- Cooja: show that the attacks are real Contiki-NG simulations.
- VS Code: show code, result folders, figures and CSV evidence.
- Terminal: run quick reproducible commands.

Do not run all simulations live. Full Cooja batches are too slow for a viva or
presentation. Use preserved evidence and short pre-recorded Cooja clips as
backup.

## Recommended Demo Order

1. Open the project in VS Code:

   `/Users/mizzy/Dissertation_Cooja_Work/rpl-dis-flood`

2. Show the validated attack coverage table:

   `experiments/dissertation_results_summary_v1/attack_coverage_table.csv`

3. Open one Cooja config, preferably Sybil:

   `experiments/sybil_attack_v1/configs/SYBIL_ATTACK_N16_SEED123456.csc`

4. Show preserved Sybil evidence:

   `experiments/sybil_attack_v1/validation_summary.csv`

5. Show concept drift:

   `experiments/dissertation_results_summary_v1/figures/static_drift_zero_recall.svg`

6. Show adaptation:

   `experiments/dissertation_results_summary_v1/figures/overall_adaptation_curve.svg`

7. Show Sybil contribution:

   `experiments/dissertation_results_summary_v1/figures/sybil_static_vs_adapted.svg`

8. Run the LLM explanation pipeline commands from `terminal_commands.md`.

9. Explain the core claim:

   Static IDS models often fail when the attack mechanism changes. Limited
   target-family adaptation recovers performance. Sybil provides a new
   identity-manipulation attack surface. The LLM layer explains IDS/drift/trust
   evidence; it is not the detector.

