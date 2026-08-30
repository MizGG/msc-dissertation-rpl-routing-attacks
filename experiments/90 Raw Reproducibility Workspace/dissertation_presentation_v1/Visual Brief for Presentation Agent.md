# Visual Brief for Presentation Agent

## Project and audience

Create original scientific visuals for a 30-minute MSc Cybersecurity dissertation defence by **AL-MIZAAN JAMAL**. The audience includes an RPL/6LoWPAN specialist who knows the prior adversarial-RL paper and a computer-science examiner who may not know Cooja or RPL.

The project uses **Contiki-NG and Cooja**, not a physical IoT testbed. It studies RPL attacks, cross-attack concept drift, whole-seed adaptation, a Sybil identity-manipulation extension, online drift monitoring, trust/defence limits and a local LLM explanation layer.

The visuals must make the method understandable without overselling it.

## Non-negotiable rules

- Use a clean academic style. Do not use cartoon security icons, mascots, padlocks, hacker silhouettes, glowing binary backgrounds or decorative gradients.
- Use 16:9 slide-safe compositions with generous margins and readable labels.
- Use short labels and restrained colours. Suggested meaning: blue for normal data/processes, red for attack activity, green for validated recovery/monitoring, amber for cautions or limits, grey for stored evidence.
- Use plain fonts and a white or very light background.
- Do not copy figures from Pasikhani et al. or SVELTE. Make original diagrams from this project.
- Do not invent metrics, attack markers, Cooja runs, physical hardware, energy measurements or RL success.
- Diagrams may be generated or drawn. Quantitative charts must be made from the supplied CSVs, not generated as illustrative images.
- All diagrams must clearly indicate that results are **Cooja simulation evidence**, not a physical deployment.

## Visual 1: Cooja-to-IDS system architecture

### Purpose

This is the main overview figure. It fills the role of a system architecture figure, but for this Cooja-based dissertation rather than the NetSim architecture in the professor paper.

### Placement

Use on the methodology slide, early in the deck.

### Diagram content

```text
          Cooja / Contiki-NG simulation
  Blackhole | Sinkhole | Sybil | Other RPL attacks
  five attack and five matched control seeds per family
                    |
                    v
       Logs, radio traces and generic RPL events
                    |
                    v
          60-second feature extraction
 delivery | rank | parent | DIO/DIS | route | identity
                    |
                    v
       labelled, seed-grouped simulated dataset
              /                     \
             v                       v
static cross-attack IDS     whole-seed adaptation
train on one family         add 0-3 complete target seeds
 test on another family       test only unseen target seeds
             \                     /
              v                   v
       metrics, drift monitoring and interpretation
              |
              v
 local LLM explanation layer: evidence to analyst-readable text
```

### Exact message

“Cooja produces controlled RPL evidence. The IDS and adaptation experiments use features extracted from that evidence. The LLM reads results after the IDS; it is not the IDS.”

### Visual instructions

- Make the first box the largest visual element.
- Use a simple network motif inside the Cooja box: root node, ordinary motes, node 16 in red as the attacker.
- Put attack names in a compact row, not as a long list.
- Use arrows from simulation to logs to features to analysis.
- Split at the IDS/adaptation stage, then rejoin at metrics and interpretation.
- Mark the LLM layer as optional and downstream, using a smaller outlined box.

## Visual 2: Experimental timeline and whole-seed split

### Purpose

Explain how the simulations become a fair dataset and why random row splitting was not used.

### Placement

Use after the architecture visual.

### Diagram content

```text
Simulation time
0 s                    240 s                           540 s
|----------------------|-------------------------------|
normal RPL warm-up       attack enabled                  end

60-second windows
0-60 | 60-120 | 120-180 | 180-240 | 240-300 | ... | 480-540
normal windows                          attack windows for attack runs

five complete matched seeds
123456   attack and control
234567   attack and control
345678   attack and control
456789   attack and control
567890   attack and control

Training and evaluation rule
A complete family/mode/seed group stays entirely in one split.
```

### Exact facts to show

- 16-node baseline topology.
- Node 16 is the attacker in baseline campaigns.
- Five attack and five control runs per family.
- 240-second activation.
- 540-second duration.
- 60-second feature windows.

### Visual instructions

- Use a horizontal timeline with a clear red activation marker at 240 seconds.
- Use blue windows before activation and red-tinted windows after activation.
- Show seeds as separate horizontal lanes below the timeline.
- Add a small “no random-row split” callout with a crossed-out random-shuffle icon.

## Visual 3: Sybil identity-manipulation mechanism

### Purpose

Show why Sybil is a different attack surface from Blackhole, Sinkhole and rank attacks.

### Placement

Use at the start of the Sybil section.

### Diagram content

```text
Before 240 seconds
Node 16 ---- DIO, source fd00::16 ----> neighbouring motes

After 240 seconds
same physical Node 16 ---- DIO, source fd00::f001 ----> neighbours
                      ---- DIO, source fd00::f002 ----> neighbours
                      ---- DIO, source fd00::f003 ----> neighbours

Observed by neighbours:
One radio sender, several apparent RPL source identities.
```

### Exact facts to show

- The real mote and internal RPL state remain unchanged.
- Only the IPv6 source address of outgoing RPL DIO messages is rotated.
- Attack begins after 240 seconds.
- Five attack runs produced 150-151 spoofed identity events per run.
- Five controls produced zero Sybil spoofing events.

### Visual instructions

- Draw one red physical mote labelled “Node 16”.
- Draw three or four DIO envelopes/packets leaving it, each labelled with a different `fd00::f...` address.
- Draw three ordinary neighbouring motes receiving them.
- Use a dashed outline around the apparent identities to show they are virtual, not extra physical devices.
- Avoid showing multiple attacker devices because there is only one physical attacker.

## Visual 4: Static drift, adaptation and representation

### Purpose

Make the core argument visual: static transfer fails, adaptation improves results, but only when the feature representation exposes the mechanism.

### Placement

Use as a bridge into the cross-attack heatmap and adaptation charts.

### Diagram content

```text
Train on Blackhole
forwarding-loss evidence
        |
        v
Test on Sinkhole
rank-attraction evidence
        |
        v
Coarse traffic features: attack missed
        |
add rank, parent and routing-state features
        |
        v
Whole-seed adaptation on limited Sinkhole data
        |
        v
Held-out Sinkhole detection improves
```

### Exact facts to show

- Coarse Blackhole-to-Sinkhole static result: recall 0.000, F1 0.000.
- Coarse adaptation using three seeds: recall 0.060, F1 0.098.
- Routing-aware adaptation using one, two and three seeds: F1 0.813, 0.909 and 0.973.

### Visual instructions

- Use a left-to-right cause-and-correction flow.
- Show the initial feature set in grey and the routing-aware set in blue/green.
- Use a small “missed” red indicator on the coarse stage and a “learnable” green indicator after feature expansion.
- Do not imply that all source-target pairs recover. Add a small note: “Recovery differs by attack pair.”

## Visual 5: Online drift response

### Purpose

Explain the difference between detecting a routing change and adapting a supervised model.

### Placement

Use before the online-drift result table.

### Diagram content

```text
RPL routing windows in time order
              |
       +------+------+
       |             |
       v             v
CUSUM              IDS prediction
low-rank state         |
no labels              v
       |          delayed label
       v               |
alert in attack     DDM error monitor
window              |
                    v
                alert one window later
```

### Exact facts to show

- CUSUM: 5/5 attack alerts, 0/5 control alerts, zero-window delay.
- DDM: 5/5 attack alerts, 0/5 control alerts, 60-second delay.
- CUSUM uses generic low-rank state features.
- DDM uses delayed classifier error information.

### Visual instructions

- Use two parallel paths from the same time-ordered window stream.
- Use a clock marker at 240 seconds.
- Do not show automatic live retraining in Contiki. The study is monitoring over saved Cooja telemetry.

## Visual 6: Local LLM explanation layer

### Purpose

Explain exactly what the LLM does and does not do.

### Placement

Use near the end of the presentation or during the live demo.

### Diagram content

```text
Cooja and IDS evidence
F1, recall, confusion matrix,
rank/parent/DIO changes, drift and trust alerts
                    |
                    v
Structured JSON evidence case
                    |
                    v
Local Qwen model through Ollama
                    |
                    v
Analyst-readable explanation
what changed | why static IDS struggled |
uncertainty | recommended next check
```

### Exact facts to show

- Model: local `qwen2.5:3b` through Ollama.
- No API key or cloud API is required after the model download.
- Nine real local explanations were generated.
- Rule-based screening: 9 valid responses, mean 7.7778/10, no unsupported-claim penalties.

### Visual instructions

- Make the structured evidence record look like a small neutral document or table, not a chat bubble full of invented text.
- Place “LLM is not IDS or drift detector” directly under the LLM box.
- Do not use OpenAI logos or cloud-service logos.

## Data charts: use real project files only

These should be clean charts, not generated illustrations.

### Chart A: Cross-attack F1 heatmap

- Source: `dissertation_final_figures_v2/tables/cross_attack_cart_f1.csv`.
- Rows: source training family.
- Columns: target test family.
- Colour: F1 from red/low to green/high.
- State: 48 of 72 cross-attack CART pairs have zero recall; only 6 have F1 >= 0.80.
- Use on the core concept-drift slide.

### Chart B: Whole-seed adaptation curve

- Source: cross-attack adaptation summary CSV.
- X-axis: 0, 1, 2, 3 target seeds used for adaptation.
- Y-axis: F1 and optionally recall as separate lines.
- Use mean results: F1 0.1822, 0.8258, 0.8664, 0.8792.
- Use on the adaptation slide.

### Chart C: Sybil attack-rate comparison

- Source: `sybil_rate_campaign_metrics.csv`.
- Show control, low-rate Sybil and high-rate Sybil.
- Primary bar: spoofed DIO markers per run, 0, 29 and 299.
- Secondary annotation: total radio TX means, 8,984, 9,020 and 9,301.
- Use on the Sybil sensitivity slide.

### Chart D: Trust and defence cost

- Source: `sinkhole_defence_operational_cost.csv`.
- Compare control, Sinkhole attack and rank-parent defence.
- Show application responses and radio transmissions as separate panels or a paired chart.
- State the negative outcome: rank-parent defence reduced responses by 79.1% and increased radio TX by 571.2% in the tested topology.
- Use on the critical-reflection slide.

## Output requirements

Create editable PowerPoint-native diagrams where possible. For charts, keep the source CSV beside the generated chart. Use SVG or high-resolution PNG for any non-native graphic. Provide a brief source note for every result figure, naming the CSV used.
