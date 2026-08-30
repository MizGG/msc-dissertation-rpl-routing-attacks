# Presentation Guide: 30 Minutes

This guide explains the purpose of each slide in `Al-Mizaan_Jamal_Dissertation_Presentation_v2.pptx` and gives a practical way to present it to both an RPL specialist and a computer-science examiner who may not know Cooja.

## The story in one sentence

An IDS trained on one RPL attack does not reliably recognise a different attack mechanism. Whole-seed adaptation can recover performance when the features expose the new mechanism. Sybil adds a distinct identity-based attack surface, while the trust, defence and RL experiments show where simple extensions still fall short.

## Recommended running order

| Section | Slides | Target time |
|---|---:|---:|
| Problem, context and literature | 1-5 | 5 min |
| Cooja method and data | 6-9 | 5 min |
| Core concept-drift results | 10-14 | 7 min |
| Sybil contribution and adaptation | 15-18 | 5 min |
| Online response, robustness and limitations | 19-23 | 5 min |
| Demo or recorded clip | 24 | 2-3 min |
| Conclusion and questions | 25 | 1-2 min |

Aim for 24-26 minutes of slides. Use the remaining time for a short demo, questions during the talk, or a recorded fallback. Do not attempt to run a full 540-second simulation live.

## Slide-by-slide plan

### Slide 1: Title

**What it does:** Opens with the actual topic and names the three main parts of the work: concept drift, Sybil and operational evaluation.

**Say:** “This project asks whether an RPL intrusion detector still works when the attack behaviour changes. I test that question in Contiki-NG and Cooja, then examine adaptation, a Sybil identity attack, and the practical limits of defence.”

**Time:** 20 seconds.

### Slide 2: Problem, evidence and contribution

**What it does:** Gives the examiner a map of the dissertation before technical detail starts.

**Say:** Explain the five questions in order: static generalisation, target-data adaptation, the new Sybil surface, online response, and robustness. End on the central point: adaptation alone is not enough if the feature set cannot see the changed attack mechanism.

**Time:** 1 minute.

### Slide 3: RPL security context

**What it does:** Brings a non-specialist up to speed on RPL, rank, the DODAG root and the kinds of behaviour attacks can change.

**Say:** “RPL builds a routing graph towards a root. Different attacks affect different parts of that graph: forwarding, rank, parent choice, control-message rate, radio path or identity.” Point to the four groups of attacks and their observables.

**Important:** Do not teach every RPL packet type. The purpose is to show why one generic traffic feature set may miss a route or identity attack.

**Time:** 1.5 minutes.

### Slide 4: Relationship to SVELTE and Gope et al.

**What it does:** Positions the work honestly against the two key papers.

**Say:** SVELTE motivates protocol-aware RPL observables and Cooja validation. Gope et al. motivates evolving attack profiles, drift and adaptive IDS ideas. This project uses Contiki-NG/Cooja to create controlled firmware-level evidence rather than claiming an exact NetSim adversarial-RL reproduction.

**Time:** 1 minute.

### Slide 5: NetSim versus Cooja

**What it does:** Answers why the project did not simply reproduce the Gope architecture in NetSim.

**Say:** NetSim is useful for larger network-level adaptive scenarios. Cooja is useful here because it executes real Contiki-NG RPL/application code and provides detailed protocol logs. The trade-off is a smaller campaign and no physical-radio validation.

**Time:** 1 minute.

### Slide 6: Experimental protocol

**What it does:** Establishes fairness and repeatability before results are shown.

**Say:** Every baseline family uses a 16-node topology, five attack seeds, five controls, 240-second activation and 540-second duration. The 60-second windows are the unit of observation, but the seed/run is the unit of train-test separation.

**Important:** State clearly that random row splitting would leak windows from the same run into both training and testing.

**Time:** 1 minute.

### Slide 7: Attack implementation and validation evidence

**What it does:** Shows that the IDS work rests on validated simulations rather than assumed labels.

**Say:** “Before training any model, I checked that every attack activated and produced the expected protocol-level evidence.” Give two or three examples: Blackhole suppresses delivery, Sinkhole advertises low rank, Sybil produces rotating DIO identities. Then state the total: 45 attack and 45 control baseline runs.

**Time:** 1.5 minutes.

### Slide 8: Frozen dataset and provenance controls

**What it does:** Explains how Cooja logs became a dataset without leaking labels or attack markers into the classifier.

**Say:** The dataset has 810 60-second windows from 90 run groups. Predictive features are generic routing/network measurements. Run identifiers, attack activation markers and labels are not predictors.

**Time:** 1 minute.

### Slide 9: IDS evaluation stack

**What it does:** Prevents the later model results from being confused as one single system.

**Say:** Static CART/Gaussian models answer the transfer question. Whole-seed adaptation answers how much new labelled data is needed. CUSUM/DDM answer when a change may be noticed. Incremental and RL controllers are extensions. The identity monitor answers a Sybil-specific observability question.

**Time:** 1.5 minutes.

### Slide 10: Static cross-attack transfer matrix

**What it does:** Presents the main concept-drift result.

**Say:** “Training on one attack and testing on another fails frequently. Forty-eight of 72 off-diagonal CART pairs have zero attack recall, and only six have F1 at least 0.8.” Explain that this is a controlled cross-attack distribution shift, not proof of uncontrolled real-world drift.

**Time:** 1 minute.

### Slide 11: Static models agree on the failure

**What it does:** Shows that the result is not just a CART artefact.

**Say:** CART is stronger than the Gaussian baseline, but both struggle. Accuracy is not the focus because normal and pre-attack windows can dominate the data. Recall and F1 reveal missed attack windows.

**Time:** 1 minute.

### Slide 12: Feature representation changed the Sinkhole conclusion

**What it does:** Shows an important correction in the work, not just a positive result.

**Say:** Early coarse traffic features failed for Blackhole-to-Sinkhole even after adaptation. Sinkhole manipulates rank and route attraction, so I added rank, parent and routing-state evidence. With those features, adaptation became effective.

**Key message:** The lesson is not “retraining always fixes drift.” The lesson is “retraining needs a representation that exposes the new mechanism.”

**Time:** 1.5 minutes.

### Slide 13: Whole-seed adaptation curve

**What it does:** Shows the overall recovery pattern across all nine families.

**Say:** With no target data, mean F1 is 0.182. One complete target seed gives the largest improvement, then two and three seeds improve more gradually. All evaluation seeds remain unseen.

**Time:** 1 minute.

### Slide 14: Adaptation is heterogeneous

**What it does:** Stops the audience from assuming the average curve applies to every pair.

**Say:** Point out one clean recovery, one non-monotonic pair and the DIS-flood to DIO-suppression failure. Similar mechanisms transfer more easily; some changed mechanisms remain invisible to the current representation.

**Time:** 1 minute.

### Slide 15: Why Sybil is a meaningful new attack surface

**What it does:** Justifies Sybil as the project’s original extension.

**Say:** The work does not claim to invent Sybil attacks. Its contribution is a controlled Cooja implementation and evaluation of identity manipulation within the same drift/adaptation framework. One physical node produces several apparent DIO identities, which changes the evidence from delivery/rank to identity consistency.

**Time:** 1 minute.

### Slide 16: Sybil rate campaign

**What it does:** Shows that Sybil was tested at more than one intensity.

**Say:** Low rate and high rate produce different spoofed-DIO counts and different radio loads. This validates that the implementation is controllable and that a stronger signal may also be easier to detect.

**Time:** 1 minute.

### Slide 17: Sybil detection and adaptation evidence

**What it does:** Presents the main Sybil result.

**Say:** Static cross-family transfer to Sybil is weak. One held-out adaptation seed gives high F1. Separately, the transparent identity monitor detects every post-activation Sybil window and no control windows in this controlled address plan.

**Important:** The identity monitor is a specific observable, not a general deployed Sybil defence.

**Time:** 1 minute.

### Slide 18: Adaptive-controller extension

**What it does:** Reports the RL result honestly.

**Say:** The isolated DQN/DDQN controllers were feasible, but neither beat the simple always-incremental baseline. The stream is small and the policy/reward space is limited. This is a useful negative result, not a claim that RL is superior.

**Time:** 1 minute.

### Slide 19: Online drift detection

**What it does:** Separates detecting change from adapting after it.

**Say:** CUSUM sees the mechanism-aware low-rank signal in the same window. DDM detects after a one-window delay because it needs classifier errors and delayed labels. Both alert on all five Sinkhole attacks and no controls in this experiment.

**Time:** 1 minute.

### Slide 20: Robustness under relocation and loss

**What it does:** Tests whether the conclusion depends entirely on one topology and radio setting.

**Say:** Under attacker relocation and a lower radio reception probability, three-seed adaptation remains high. Sybil under loss is slightly weaker and has a small false-positive rate. This is stronger than one baseline topology, but it is still simulation evidence.

**Time:** 1 minute.

### Slide 21: Trust features and active defence

**What it does:** Shows that extra complexity did not automatically improve the system.

**Say:** Offline trust features help explain which type of abnormality is present, but they do not improve F1 over routing features. The active Sinkhole defence catches forged rank but causes severe parent churn and radio overhead. The right result to report is that safe routing intervention needs hysteresis and stability controls.

**Time:** 1 minute.

### Slide 22: External Gope data

**What it does:** Adds an external comparison without pretending the datasets are identical.

**Say:** The Gope data shows the same direction of failure for Blackhole-to-Sinkhole transfer: low recall and F1. The numbers are not directly comparable because the simulator, labels, features and split unit differ.

**Time:** 1 minute.

### Slide 23: What failed and how the work improved

**What it does:** This is the critical-reflection slide. It demonstrates research maturity.

**Say:** Walk through the corrections: coarse features missed rank manipulation, random-row leakage was avoided through seed grouping, trust was reframed as diagnostic, the defence was reported as harmful, and the RL controller was compared fairly against a simple baseline.

**Time:** 1.5 minutes.

### Slide 24: Live demonstration and recorded fallback

**What it does:** Explains the demo plan without relying on the demo to prove the research.

**Say:** Show a validated Sybil configuration in Cooja and one activation/identity marker. Then show the matching validation summary and, if time permits, the local LLM evidence-to-explanation command. Use recorded clips if Cooja is slow.

**Recommended live demo:** 2-3 minutes total. Show one Sybil attack only. Keep 45-90 second clips for Control, Blackhole, Sinkhole and Sybil as fallbacks.

### Slide 25: Conclusions

**What it does:** Ends with evidence, not future promises.

**Say:** Repeat five conclusions: static transfer is brittle; one representative target seed usually gives the largest recovery; mechanism-aware features determine whether adaptation can work; Sybil is a distinct identity surface; and operational work shows detection accuracy is not enough for safe routing intervention.

**Time:** 1 minute, then invite questions.

## Questions you should be ready for

- **Why Cooja instead of a physical testbed?** Cooja provided controlled, repeatable firmware-level RPL behaviour within the project scope. The limitation is stated clearly: results are not physical-deployment validation.
- **Did you reproduce Gope et al. exactly?** No. The project is a Cooja-based controlled extension inspired by their drift/adaptation architecture. The NetSim RL architecture was not reproduced exactly.
- **Why use five seeds?** Five matched seeds balance repeatability with simulation cost. All train/test decisions preserve complete seed groups.
- **Is the LLM part of the IDS?** No. It converts structured IDS, drift, adaptation and trust evidence into a readable analyst explanation.
- **Does the trust layer solve Sinkhole?** No. The offline trust features helped interpretation but did not improve F1, and the active defence had unacceptable routing cost.
- **Does RL outperform conventional adaptation?** No. The current controllers did not beat always-incremental updating. This is reported as a limitation.
