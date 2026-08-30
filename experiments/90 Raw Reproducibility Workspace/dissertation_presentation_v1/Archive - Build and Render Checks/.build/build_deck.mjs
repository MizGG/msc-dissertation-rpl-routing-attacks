import fs from "node:fs/promises";
import { readFileSync } from "node:fs";
import { Presentation, PresentationFile } from "@oai/artifact-tool";

const ROOT = "/Users/mizzy/Dissertation_Cooja_Work/rpl-dis-flood";
const OUT = `${ROOT}/experiments/dissertation_presentation_v1/Al-mizan_Jamal_Dissertation_Presentation_v1.pptx`;
const BUILD = `${ROOT}/experiments/dissertation_presentation_v1/.build`;
const ASSET = `${BUILD}/assets`;
const PAPER_SHOT = "/Users/mizzy/Desktop/Screenshot 2026-08-29 at 12.31.40.png";

const C = {
  ink: "#101828", muted: "#475467", soft: "#F2F4F7", line: "#D0D5DD",
  white: "#FFFFFF", teal: "#087E8B", blue: "#2563EB", amber: "#D97706",
  red: "#C2413B", green: "#198754", navy: "#15253D", pale: "#E8F5F6",
};
const FONT = "Aptos";
const pres = Presentation.create({ slideSize: { width: 1280, height: 720 } });

function box(slide, x, y, w, h, fill = C.white, line = "none", radius = 0) {
  return slide.shapes.add({ geometry: radius ? "roundRect" : "rect", position: { left: x, top: y, width: w, height: h }, fill,
    line: { style: "solid", fill: line, width: line === "none" ? 0 : 1 }, ...(radius ? { borderRadius: radius } : {}) });
}

function text(slide, value, x, y, w, h, size = 22, color = C.ink, bold = false, align = "left") {
  const s = slide.shapes.add({ geometry: "textbox", position: { left: x, top: y, width: w, height: h }, fill: "none",
    line: { style: "solid", fill: "none", width: 0 } });
  s.text = value;
  s.text.style = { fontFamily: FONT, fontSize: size, color, bold, alignment: align, verticalAlignment: "middle" };
  return s;
}

function line(slide, x, y, w, h = 2, fill = C.line) { return box(slide, x, y, w, h, fill, "none"); }
function circle(slide, x, y, d, fill, label, size = 18, color = C.white) {
  const c = slide.shapes.add({ geometry: "ellipse", position: { left: x, top: y, width: d, height: d }, fill,
    line: { style: "solid", fill: C.white, width: 2 } });
  const t = text(slide, label, x, y, d, d, size, color, true, "center");
  return [c, t];
}
function footer(slide, n, section = "MSc dissertation") {
  line(slide, 64, 682, 1152, 1, C.line);
  text(slide, section, 64, 687, 300, 18, 11, C.muted, false);
  text(slide, String(n).padStart(2, "0"), 1160, 687, 56, 18, 11, C.muted, true, "right");
}
function title(slide, t, sub, n, section) {
  text(slide, t, 64, 42, 1040, 50, 36, C.ink, true);
  if (sub) text(slide, sub, 64, 94, 1100, 34, 17, C.muted, false);
  line(slide, 64, 132, 88, 5, C.teal);
  footer(slide, n, section);
}
function addNotes(slide, talk, sources = []) {
  const block = sources.length ? `\n\n[Sources]\n${sources.map((s) => `- ${s}`).join("\n")}\n[/Sources]` : "";
  slide.speakerNotes.textFrame.setText(`${talk}${block}`);
  slide.speakerNotes.setVisible(true);
}
function metric(slide, x, y, w, number, label, color = C.teal, size = 46) {
  text(slide, number, x, y, w, 66, size, color, true);
  text(slide, label, x, y + 67, w, 55, 17, C.muted, false);
}
function bullet(slide, x, y, w, value, color = C.ink, size = 20) {
  box(slide, x, y + 10, 8, 8, C.teal, "none", 4);
  text(slide, value, x + 22, y, w - 22, 54, size, color, false);
}
function image(slide, path, x, y, w, h, fit = "contain", crop = undefined, alt = "") {
  const contentType = path.toLowerCase().endsWith(".jpg") || path.toLowerCase().endsWith(".jpeg") ? "image/jpeg" : "image/png";
  return slide.images.add({ blob: readFileSync(path), contentType, alt, fit, position: { left: x, top: y, width: w, height: h }, ...(crop ? { crop } : {}) });
}
function pill(slide, value, x, y, w, fill, color = C.white) {
  box(slide, x, y, w, 32, fill, "none", 16);
  text(slide, value, x, y, w, 32, 14, color, true, "center");
}

// 1. Title
{
  const s = pres.slides.add(); s.background.fill = C.navy;
  box(s, 0, 0, 18, 720, C.teal);
  text(s, "RPL IDS under\ncontrolled concept drift", 78, 126, 760, 190, 54, C.white, true);
  text(s, "Attack reproduction, Sybil extension, adaptation and operational limits", 82, 342, 760, 74, 24, "#D0D5DD");
  line(s, 82, 444, 470, 2, "#4A607D");
  text(s, "Al-mizan Jamal", 82, 472, 440, 42, 24, C.white, true);
  text(s, "MSc Cybersecurity dissertation presentation", 82, 514, 560, 34, 18, "#BFC9D8");
  circle(s, 934, 164, 128, C.teal, "RPL", 32);
  circle(s, 1024, 278, 94, C.blue, "IDS", 24);
  circle(s, 872, 326, 112, C.amber, "DRIFT", 20);
  line(s, 978, 274, 70, 4, "#79D7DA"); line(s, 924, 292, 34, 55, "#79D7DA");
  text(s, "Contiki-NG + Cooja", 904, 472, 260, 32, 17, "#D0D5DD", true, "center");
  addNotes(s, "Timing: 0:00-0:30. Introduce yourself and the central topic. State that the talk is designed for both an RPL specialist and a general computer-science audience. The project studies what happens when an IDS trained on one RPL attack encounters a different attack mechanism.");
}

// 2. Headline result
{
  const s = pres.slides.add(); s.background.fill = C.white; title(s, "The result in one sentence", "Static detection is brittle, but limited whole-run adaptation often recovers performance.", 2, "Finding");
  metric(s, 76, 188, 300, "48 / 72", "cross-attack CART pairs had zero attack recall", C.red);
  metric(s, 458, 188, 300, "0.182 → 0.826", "mean F1 after adding one target-family seed", C.teal, 37);
  metric(s, 840, 188, 300, "0.218 → 0.968", "Sybil target F1 after one adaptation seed", C.blue, 37);
  box(s, 76, 458, 1064, 116, C.soft, "none", 6);
  text(s, "Core claim", 100, 478, 160, 28, 16, C.teal, true);
  text(s, "Retraining is not enough when the feature representation does not expose the changed attack mechanism.", 100, 516, 980, 40, 25, C.ink, true);
  addNotes(s, "Timing: 0:30-1:30. Lead with the conclusion. Zero recall means the classifier missed every attack observation in that train-test pairing. Explain that the improvement uses complete simulation seeds, not random rows, which reduces leakage.", [
    `${ROOT}/experiments/dissertation_results_summary_v1/concept_drift_key_metrics.csv`,
    `${ROOT}/experiments/dissertation_results_summary_v1/adaptation_key_metrics.csv`
  ]);
}

// 3. Primer
{
  const s = pres.slides.add(); s.background.fill = C.white; title(s, "RPL and Cooja in 90 seconds", "A routing protocol for constrained networks, evaluated in a repeatable simulator.", 3, "Primer");
  circle(s, 102, 198, 80, C.navy, "ROOT", 18);
  circle(s, 330, 184, 68, C.teal, "2", 19); circle(s, 330, 374, 68, C.teal, "3", 19);
  circle(s, 570, 170, 62, C.blue, "4", 18); circle(s, 570, 286, 62, C.blue, "5", 18); circle(s, 570, 414, 62, C.blue, "6", 18);
  line(s, 178, 236, 74, 4, C.line); box(s, 250, 216, 4, 194, C.line); line(s, 252, 216, 82, 4, C.line); line(s, 252, 406, 82, 4, C.line);
  line(s, 394, 216, 98, 4, C.line); box(s, 490, 198, 4, 120, C.line); line(s, 492, 198, 82, 4, C.line); line(s, 492, 316, 82, 4, C.line); line(s, 394, 406, 180, 4, C.line);
  text(s, "Ranks guide nodes toward the root", 88, 510, 540, 38, 20, C.muted, true, "center");
  box(s, 716, 166, 444, 388, C.soft, "none", 6);
  text(s, "Why Cooja?", 748, 196, 360, 38, 26, C.ink, true);
  bullet(s, 748, 250, 368, "Runs real Contiki-NG firmware logic", C.ink, 19);
  bullet(s, 748, 316, 368, "Controls topology, radio model, seed and timing", C.ink, 19);
  bullet(s, 748, 382, 368, "Produces inspectable logs and repeatable evidence", C.ink, 19);
  text(s, "Not a physical deployment", 748, 480, 336, 28, 16, C.amber, true);
  text(s, "Results establish simulator-level validity, not hardware generalisation.", 748, 508, 350, 40, 16, C.muted);
  addNotes(s, "Timing: 1:30-2:50. RPL forms a destination-oriented directed acyclic graph. Nodes advertise rank and select parents toward a root. Cooja emulates the network and executes Contiki-NG code. Clarify that this is a simulation study, so radio and timing control are strengths, while physical deployment validity remains outside scope.", [
    `${ROOT}/experiments/dissertation_overleaf_v1/chapters/03_methodology.tex`
  ]);
}

// 4. Threat surface
{
  const s = pres.slides.add(); s.background.fill = C.white; title(s, "Nine attack families, four mechanisms", "The experimental set spans data, routing, control and identity behaviour.", 4, "Threat model");
  const cols = [76, 360, 644, 928];
  const heads = ["FORWARDING", "RANK + ROUTE", "CONTROL PLANE", "IDENTITY"];
  const fills = [C.red, C.amber, C.teal, C.blue];
  const items = [["Blackhole", "Grayhole"], ["Sinkhole", "Increase rank", "Worst parent", "Wormhole"], ["DIS flood", "DIO suppression"], ["Sybil"]];
  for (let i = 0; i < 4; i++) {
    pill(s, heads[i], cols[i], 174, 220, fills[i]);
    items[i].forEach((v, j) => { line(s, cols[i], 234 + j * 72, 220, 1, C.line); text(s, v, cols[i] + 6, 248 + j * 72, 210, 42, 21, C.ink, true); });
  }
  box(s, 76, 538, 1072, 64, C.pale, "none", 4);
  text(s, "Concept drift is induced by changing the attack mechanism between training and evaluation.", 100, 548, 1020, 42, 22, C.navy, true, "center");
  addNotes(s, "Timing: 2:50-4:00. Explain that the attacks are not interchangeable. A blackhole drops packets; a sinkhole advertises an attractive rank; Sybil injects changing identities. Training on one mechanism and testing on another creates a controlled attack-distribution change.", [
    `${ROOT}/experiments/dissertation_results_summary_v1/attack_coverage_table.csv`
  ]);
}

// 5. Questions and contribution
{
  const s = pres.slides.add(); s.background.fill = C.white; title(s, "Research questions", "The work moves from reproduction to drift, adaptation and a new attack surface.", 5, "Scope");
  const qs = [
    ["RQ1", "How well does a static IDS generalise across RPL attack families?"],
    ["RQ2", "How much whole-seed target data is needed to recover performance?"],
    ["RQ3", "Does Sybil expose a distinct and useful identity-based drift target?"],
    ["RQ4", "How do radio changes, relocation and defensive controls affect conclusions?"]
  ];
  qs.forEach((q, i) => { const y = 166 + i * 104; text(s, q[0], 80, y, 88, 44, 25, C.teal, true); line(s, 170, y + 20, 48, 3, C.teal); text(s, q[1], 244, y - 2, 900, 54, 23, C.ink, i === 2); });
  addNotes(s, "Timing: 4:00-5:05. These questions keep the contribution narrow and defensible. RQ3 is the originality point: Sybil is not merely a ninth row in the table. It changes the observable mechanism to identity manipulation and therefore tests whether the representation can follow a new security surface.", [
    `${ROOT}/experiments/dissertation_overleaf_v1/chapters/01_introduction.tex`
  ]);
}

// 6. Literature lineage
{
  const s = pres.slides.add(); s.background.fill = C.white; title(s, "How the prior work shaped this study", "Two papers provide the security and adaptation foundations.", 6, "Research lineage");
  const xs = [74, 432, 790];
  const years = ["2013", "2022", "THIS STUDY"];
  const names = ["SVELTE", "Gope et al.", "Controlled Cooja extension"];
  const body = [
    "RPL-aware intrusion detection\nSinkhole and selective forwarding\nContiki/Cooja evaluation",
    "Evolving 6LoWPAN environment\nARL + DQN/DDQN + DDM\nNetSim attack profiles",
    "Nine firmware-level attacks\nCross-family drift + whole-seed adaptation\nSybil, robustness and negative results"
  ];
  for (let i = 0; i < 3; i++) {
    text(s, years[i], xs[i], 172, 300, 34, 16, i === 2 ? C.teal : C.muted, true);
    text(s, names[i], xs[i], 214, 310, 46, 27, C.ink, true);
    line(s, xs[i], 270, 292, 4, i === 2 ? C.teal : C.line);
    text(s, body[i], xs[i], 298, 300, 150, 18, C.muted);
  }
  line(s, 150, 500, 830, 3, C.line); circle(s, 137, 486, 30, C.navy, "", 1); circle(s, 495, 486, 30, C.navy, "", 1); circle(s, 853, 486, 30, C.teal, "", 1);
  box(s, 74, 552, 1076, 56, C.soft, "none", 4); text(s, "Claimed relationship: extension and comparison, not a full reproduction of the paper's RL architecture.", 92, 560, 1040, 38, 18, C.ink, true, "center");
  addNotes(s, "Timing: 5:05-6:20. SVELTE established that RPL-specific routing evidence can support intrusion detection. Gope and colleagues made adaptation under evolving attack distributions central. This dissertation adopts that question but changes the experimental route: real Contiki-NG application logic in Cooja, controlled attack-family transfer, simpler interpretable models and whole-seed evaluation. Do not claim architectural superiority or full reproduction.", [
    "/Users/mizzy/Downloads/2013-Elsevier-SVELTE realtime ID in the IoT.pdf",
    "/Users/mizzy/Documents/Dissertation/diss papers/Adversarial_RL-Based_IDS_for_Evolving_Data_Environment_in_6LoWPAN.pdf"
  ]);
}

// 7. Method comparison with image
{
  const s = pres.slides.add(); s.background.fill = C.white; title(s, "Same problem, different experimental route", "The paper studies adaptive agents; this dissertation isolates generalisation and adaptation behaviour.", 7, "Method comparison");
  image(s, PAPER_SHOT, 66, 158, 500, 350, "cover", { left: 0.055, top: 0.12, right: 0.47, bottom: 0.31 }, "Gope et al. adversarial RL architecture figure");
  text(s, "Gope et al.", 66, 524, 500, 30, 17, C.navy, true, "center");
  text(s, "NetSim • adversarial RL • DQN/DDQN • DDM", 66, 554, 500, 28, 15, C.muted, false, "center");
  line(s, 620, 170, 2, 410, C.line);
  text(s, "This dissertation", 678, 170, 474, 38, 27, C.teal, true);
  bullet(s, 678, 230, 468, "Contiki-NG applications executed in Cooja", C.ink, 18);
  bullet(s, 678, 294, 468, "Cross-attack transfer matrix as controlled drift", C.ink, 18);
  bullet(s, 678, 358, 468, "CART and Gaussian baselines plus incremental studies", C.ink, 18);
  bullet(s, 678, 422, 468, "Whole-seed adaptation prevents within-run leakage", C.ink, 18);
  box(s, 678, 506, 450, 82, C.pale, "none", 4);
  text(s, "Advantage: firmware-level inspectability\nLimitation: less sophisticated adaptive policy", 696, 518, 420, 58, 17, C.navy, true);
  addNotes(s, "Timing: 6:20-7:45. The left figure is the paper's architecture. NetSim supports scalable network-level experiments and the authors' adversarial RL formulation. Cooja gives closer integration with Contiki-NG firmware and explicit protocol hooks. These are different methodological strengths. Our adaptation curve is empirical retraining with whole seeds, not the paper's DQN/DDQN policy-learning mechanism.", [
    "/Users/mizzy/Documents/Dissertation/diss papers/Adversarial_RL-Based_IDS_for_Evolving_Data_Environment_in_6LoWPAN.pdf",
    `${ROOT}/experiments/dissertation_overleaf_v1/chapters/03_methodology.tex`
  ]);
}

// 8. Experiment design
{
  const s = pres.slides.add(); s.background.fill = C.white; title(s, "Controlled experiment design", "Matched controls and delayed activation separate normal and attack periods.", 8, "Methodology");
  line(s, 104, 304, 1012, 6, C.line);
  circle(s, 92, 278, 58, C.navy, "0s", 16); circle(s, 512, 272, 70, C.amber, "240s", 16); circle(s, 1070, 278, 58, C.teal, "540s", 16);
  pill(s, "NORMAL WARM-UP", 184, 234, 250, C.navy); pill(s, "ATTACK ACTIVE", 660, 234, 272, C.red);
  text(s, "same topology • same seed • attack flag off", 174, 342, 284, 64, 17, C.muted, false, "center");
  text(s, "attack application changes one mechanism", 650, 342, 300, 64, 17, C.muted, false, "center");
  const vals = [["9", "families"], ["5 + 5", "attack + control runs per family"], ["90", "validated baseline simulations"], ["60 s", "feature window"]];
  vals.forEach((v, i) => metric(s, 76 + i * 280, 462, 240, v[0], v[1], i === 2 ? C.teal : C.ink));
  addNotes(s, "Timing: 7:45-9:00. Each run lasts 540 simulated seconds. The attack activates at 240 seconds. Every family has five attack and five matched control seeds. Explain why matching matters: it reduces the chance that topology or random seed, rather than the attack, explains the result.", [
    `${ROOT}/experiments/dissertation_results_summary_v1/attack_coverage_table.csv`,
    `${ROOT}/experiments/dissertation_overleaf_v1/chapters/03_methodology.tex`
  ]);
}

// 9. Dataset pipeline
{
  const s = pres.slides.add(); s.background.fill = C.white; title(s, "From simulation to frozen dataset", "Provenance and run-level grouping are treated as part of the method.", 9, "Data pipeline");
  const steps = [["COOJA", "logs + markers"], ["WINDOW", "60-second features"], ["FREEZE", "810 rows • 90 groups"], ["SPLIT", "whole simulation seeds"], ["EVALUATE", "static → adapted"]];
  steps.forEach((v, i) => {
    const x = 56 + i * 242;
    circle(s, x + 66, 212, 74, i === 4 ? C.teal : C.navy, String(i + 1), 22);
    text(s, v[0], x, 306, 206, 28, 17, C.ink, true, "center");
    text(s, v[1], x, 342, 206, 50, 16, C.muted, false, "center");
    if (i < 4) { line(s, x + 142, 248, 90, 3, C.line); text(s, ">", x + 218, 230, 30, 36, 25, C.muted, true, "center"); }
  });
  box(s, 100, 472, 1080, 98, C.soft, "none", 4);
  text(s, "Leakage control", 124, 488, 180, 26, 16, C.teal, true);
  text(s, "Attack markers and provenance identify ground truth but are excluded from predictive features.", 124, 522, 1000, 34, 21, C.ink, true);
  addNotes(s, "Timing: 9:00-10:00. There are 810 fixed windows and 90 run groups. Provenance identifies family, seed and condition. Attack markers support validation and labels but are excluded from training. The crucial split is by complete seed so near-identical windows from the same simulation cannot enter both training and testing.", [
    `${ROOT}/experiments/final_simulated_dataset_v1/evaluation_protocol.md`,
    `${ROOT}/experiments/final_simulated_dataset_v1`
  ]);
}

// 10. Coverage figure
{
  const s = pres.slides.add(); s.background.fill = C.white; title(s, "Attack implementation coverage", "All nine families have five attack and five control runs with validation evidence.", 10, "Validation");
  const coverage = [
    ["Blackhole", "forwarding loss"], ["Sinkhole", "rank attraction"], ["DIS flood", "control flooding"],
    ["Grayhole", "selective loss"], ["Increase rank", "rank degradation"], ["DIO suppression", "control suppression"],
    ["Worst parent", "parent selection"], ["Wormhole", "tunnel shortcut"], ["Sybil", "identity churn"]
  ];
  coverage.forEach((v, i) => {
    const col = i % 3, row = Math.floor(i / 3), x = 72 + col * 392, y = 158 + row * 126;
    box(s, x, y, 348, 92, i === 8 ? C.pale : C.soft, "none", 4);
    text(s, v[0], x + 20, y + 12, 200, 30, 20, C.ink, true);
    text(s, v[1], x + 20, y + 48, 210, 25, 15, C.muted);
    pill(s, "5 + 5", x + 258, y + 28, 70, i === 8 ? C.teal : C.navy);
  });
  text(s, "90 validated baseline Cooja runs", 76, 554, 1128, 40, 23, C.teal, true, "center");
  addNotes(s, "Timing: 10:00-10:55. Briefly scan the families. Make the status precise: this chart concerns the validated baseline campaign. Separate robustness and defence campaigns add further runs but are not folded into this count.", [
    `${ROOT}/experiments/dissertation_results_summary_v1/attack_coverage_table.csv`,
    `${ROOT}/experiments/dissertation_results_summary_v1/figures/attack_coverage.svg`
  ]);
}

// 11. Heatmap
{
  const s = pres.slides.add(); s.background.fill = C.white; title(s, "Static cross-attack detection often collapses", "Rows are training attacks; columns are unseen test attacks; colour is attack-class F1.", 11, "Main result");
  image(s, `${ASSET}/cross_attack_cart_f1_heatmap.png`, 108, 146, 780, 486, "contain", undefined, "Cross-attack CART F1 heatmap");
  box(s, 922, 176, 250, 126, C.soft, "none", 4); text(s, "48 / 72", 946, 190, 200, 52, 40, C.red, true, "center"); text(s, "zero-recall pairs", 946, 244, 200, 32, 17, C.muted, true, "center");
  box(s, 922, 330, 250, 126, C.soft, "none", 4); text(s, "0.182", 946, 344, 200, 52, 40, C.teal, true, "center"); text(s, "mean cross-attack F1", 936, 398, 220, 32, 17, C.muted, true, "center");
  text(s, "Dark cells are the evidence of poor generalisation.", 922, 494, 250, 72, 18, C.ink, true, "center");
  addNotes(s, "Timing: 10:55-12:35. Explain how to read one cell: train a binary classifier using controls plus one attack family, then test on held-out controls plus a different attack family. Forty-eight of 72 CART pairings had zero attack recall. The simpler Gaussian model was worse, with 66 zero-recall pairings. This is the central drift result.", [
    `${ROOT}/experiments/dissertation_final_figures_v2/tables/cross_attack_cart_f1.csv`,
    `${ROOT}/experiments/dissertation_results_summary_v1/concept_drift_key_metrics.csv`
  ]);
}

// 12. Why failure
{
  const s = pres.slides.add(); s.background.fill = C.white; title(s, "Why retraining can fail", "The representation must contain evidence of the new mechanism.", 12, "Interpretation");
  const x = [76, 440, 804];
  const hdr = ["BLACKHOLE", "SINKHOLE", "SYBIL"];
  const mech = ["Packets disappear", "Advertised rank changes", "Source identity rotates"];
  const obs = ["Traffic-volume features", "Rank and parent features", "Identity-diversity features"];
  for (let i = 0; i < 3; i++) {
    pill(s, hdr[i], x[i], 174, 276, [C.red, C.amber, C.blue][i]);
    text(s, mech[i], x[i], 230, 276, 52, 22, C.ink, true, "center");
    line(s, x[i] + 28, 300, 220, 2, C.line);
    text(s, "Needs", x[i], 326, 276, 26, 15, C.muted, true, "center");
    text(s, obs[i], x[i] + 18, 362, 240, 78, 19, C.teal, true, "center");
  }
  box(s, 120, 500, 1040, 82, C.navy, "none", 4);
  text(s, "Adaptation updates the model. Feature engineering decides what the model is capable of learning.", 150, 514, 980, 54, 23, C.white, true, "center");
  addNotes(s, "Timing: 12:35-13:50. This is the key explanation for the original blackhole-to-sinkhole failure. Blackhole produces a strong volume shift, while the original coarse sinkhole attack and control traffic looked similar. Adding rank, parent, control-message and identity features makes the changed mechanism visible. The lesson is not that adaptation is useless. The lesson is that adaptation cannot recover information that was never measured.", [
    `${ROOT}/experiments/ml_baseline/feature_diagnostics.csv`,
    `${ROOT}/experiments/routing_features_v1/results/RESULTS_INTERPRETATION.md`
  ]);
}

// 13. Adaptation curve
{
  const s = pres.slides.add(); s.background.fill = C.white; title(s, "One new seed changes the outcome", "Adaptation uses complete target-family runs and evaluates on unseen target seeds.", 13, "Adaptation");
  image(s, `${ASSET}/overall_adaptation_curve.png`, 96, 154, 820, 464, "contain", undefined, "Whole-seed adaptation curve");
  metric(s, 944, 188, 244, "+0.644", "absolute mean F1 gain with one seed", C.teal);
  metric(s, 944, 374, 244, "0.879", "mean F1 with three adaptation seeds", C.blue);
  addNotes(s, "Timing: 13:50-15:15. At zero target seeds, mean cross-attack F1 is 0.1822. One target seed raises it to 0.8258; two to 0.8664; three to 0.8792. The largest gain is early. Do not say one seed always solves drift: averages hide attack-specific variation, and the target seed is supervised adaptation data.", [
    `${ROOT}/experiments/dissertation_results_summary_v1/adaptation_key_metrics.csv`,
    `${ROOT}/experiments/dissertation_results_summary_v1/figures/overall_adaptation_curve.svg`
  ]);
}

// 14. Sybil
{
  const s = pres.slides.add(); s.background.fill = C.white; title(s, "Why Sybil is the new attack surface", "It tests identity manipulation, not just another variation of packet loss or rank change.", 14, "Original contribution");
  circle(s, 114, 210, 96, C.red, "1", 31); text(s, "physical attacker", 74, 318, 176, 34, 18, C.muted, true, "center");
  line(s, 210, 254, 128, 4, C.line);
  ["A", "B", "C", "D"].forEach((v, i) => { circle(s, 366 + (i % 2) * 132, 182 + Math.floor(i / 2) * 146, 76, C.blue, v, 25); });
  text(s, "multiple virtual RPL identities", 326, 492, 290, 38, 20, C.blue, true, "center");
  box(s, 676, 162, 478, 396, C.soft, "none", 6);
  bullet(s, 706, 190, 414, "Distinct mechanism: source-address and identity churn", C.ink, 18);
  bullet(s, 706, 262, 414, "Challenges forwarding-only trust because every identity starts fresh", C.ink, 18);
  bullet(s, 706, 350, 414, "Creates a demanding cross-family drift target", C.ink, 18);
  bullet(s, 706, 422, 414, "Validated: 150-151 spoofed DIO identity events per attack run", C.ink, 18);
  box(s, 676, 526, 478, 80, C.pale, "none", 4);
  text(s, "Sybil target F1: 0.218 static → 0.968 with one seed", 696, 544, 438, 44, 21, C.teal, true, "center");
  addNotes(s, "Timing: 15:15-17:05. A Sybil attacker presents several virtual identities. In this implementation, the attacker sends RPL DIO messages using rotating virtual IPv6 source identities after 240 seconds. Why use it? First, it extends beyond reproduction of the original attack set. Second, it moves the problem to identity manipulation. Third, it exposes the weakness of forwarding-only trust because each new identity can obtain a fresh trust history. Fourth, it gives a hard but learnable target: static transfer is poor, while one held-out adaptation seed produces F1 0.9683. Be precise that this is a simulated RPL Sybil mechanism, not a physical radio identity attack.", [
    `${ROOT}/experiments/sybil_attack_v1/README.md`,
    `${ROOT}/experiments/dissertation_results_summary_v1/sybil_contribution_summary.md`,
    `${ROOT}/experiments/dissertation_results_summary_v1/adaptation_key_metrics.csv`
  ]);
}

// 15. Drift detection
{
  const s = pres.slides.add(); s.background.fill = C.white; title(s, "Detecting when adaptation is needed", "Offline transfer measures failure; online detectors identify the change point.", 15, "Online response");
  image(s, `${ASSET}/online_drift_detection.png`, 88, 154, 820, 462, "contain", undefined, "Online drift detection comparison");
  text(s, "CUSUM", 950, 180, 210, 34, 22, C.teal, true, "center");
  text(s, "5/5 detected\n0/5 control alerts\nfirst post-attack window", 950, 224, 210, 100, 18, C.ink, false, "center");
  line(s, 956, 350, 198, 2, C.line);
  text(s, "DDM", 950, 378, 210, 34, 22, C.blue, true, "center");
  text(s, "5/5 detected\n0/5 control alerts\n60 s median delay", 950, 422, 210, 100, 18, C.ink, false, "center");
  addNotes(s, "Timing: 17:05-18:15. The rank-state CUSUM is mechanism-aware and reacts in the first post-activation window. DDM observes delayed classifier errors and therefore reacts later, with a 60-second median delay. This is a small five-seed evaluation, so avoid claiming universal false-alarm performance.", [
    `${ROOT}/experiments/dissertation_final_figures_v2/tables/online_drift_detection_summary.csv`,
    `${ROOT}/experiments/online_drift_response_v1/README.md`
  ]);
}

// 16. Robustness
{
  const s = pres.slides.add(); s.background.fill = C.white; title(s, "Does the result survive changed conditions?", "Attacker relocation and lossy radio stress topology-specific learning.", 16, "Robustness");
  image(s, `${ASSET}/robustness_static_vs_adapted_f1.png`, 76, 154, 850, 470, "contain", undefined, "Static versus adapted robustness F1");
  box(s, 952, 180, 224, 324, C.soft, "none", 4);
  text(s, "3-seed adapted F1", 972, 204, 184, 32, 17, C.muted, true, "center");
  text(s, "1.000", 972, 254, 184, 48, 37, C.teal, true, "center"); text(s, "blackhole + sinkhole", 972, 304, 184, 30, 16, C.muted, false, "center");
  text(s, "0.995", 972, 354, 184, 48, 37, C.blue, true, "center"); text(s, "relocated Sybil", 972, 404, 184, 30, 16, C.muted, false, "center");
  text(s, "0.937", 972, 454, 184, 48, 37, C.amber, true, "center"); text(s, "lossy-radio Sybil", 972, 504, 184, 30, 16, C.muted, false, "center");
  addNotes(s, "Timing: 18:15-19:25. The robustness campaign adds 60 runs across relocation and lossy-radio conditions for blackhole, sinkhole and Sybil. Three-seed adapted CART remains strong, but lossy-radio Sybil is the weakest case and has FPR 0.0462. This is evidence that radio uncertainty still matters.", [
    `${ROOT}/experiments/dissertation_final_figures_v2/tables/robustness_static_vs_adapted.csv`,
    `${ROOT}/experiments/robustness_campaign_v4/results_summary.md`
  ]);
}

// 17. Trust layer
{
  const s = pres.slides.add(); s.background.fill = C.white; title(s, "Trust is useful evidence, not a universal defence", "A multi-signal trust layer must match the mechanism being monitored.", 17, "Trust layer");
  const layers = [["Forwarding", "blackhole • grayhole", C.red], ["Rank", "sinkhole • rank attacks", C.amber], ["Control", "DIS • DIO behaviour", C.teal], ["Identity", "Sybil resistance", C.blue]];
  layers.forEach((v, i) => { const y = 170 + i * 92; box(s, 98, y, 420, 66, v[2], "none", 4); text(s, v[0], 122, y + 10, 160, 46, 22, C.white, true); text(s, v[1], 274, y + 10, 220, 46, 16, C.white, false, "right"); });
  line(s, 610, 172, 2, 360, C.line);
  text(s, "What the experiment showed", 670, 170, 440, 40, 25, C.ink, true);
  bullet(s, 670, 236, 440, "Trust features improved interpretability of attack surfaces", C.ink, 18);
  bullet(s, 670, 316, 440, "They did not improve predictive metrics in the current evaluation", C.ink, 18);
  bullet(s, 670, 414, 440, "Sybil requires identity persistence or authentication, not fresh scores", C.ink, 18);
  box(s, 670, 514, 430, 72, C.soft, "none", 4); text(s, "Defensible claim: diagnostic layer, not complete prevention", 692, 526, 390, 46, 19, C.teal, true, "center");
  addNotes(s, "Timing: 19:25-20:25. The original forwarding-trust idea is strong for blackhole and useful for grayhole. It is incomplete for sinkhole, DIS flooding, wormhole and Sybil. The project therefore treats trust as a structured evidence layer. The measured trust features did not improve model performance, so the correct claim is interpretability support, not a universal defence.", [
    `${ROOT}/experiments/trust_layer_v1/results/trust_layer_interpretation.md`,
    `${ROOT}/experiments/dissertation_results_summary_v1/trust_layer_summary.md`
  ]);
}

// 18. Negative defence result
{
  const s = pres.slides.add(); s.background.fill = C.white; title(s, "When defence damages the network", "The sinkhole rejection policy produced an important negative result.", 18, "Defence evaluation");
  image(s, `${ASSET}/sinkhole_defence_operational_cost.png`, 76, 154, 850, 462, "contain", undefined, "Sinkhole defence operational cost");
  metric(s, 958, 178, 220, "−79%", "application responses versus control", C.red);
  metric(s, 958, 350, 220, "+571%", "radio transmissions versus control", C.amber);
  text(s, "681.8 mean parent switches", 952, 530, 230, 44, 18, C.ink, true, "center");
  addNotes(s, "Timing: 20:25-21:40. The defence rejected suspicious sinkhole routing evidence, but the policy was unstable. Compared with control, application responses fell by 79.06 percent and radio transmissions rose by 571.22 percent, with 681.8 average parent switches. This is not hidden as a failed experiment. It shows that correct suspicion without hysteresis, confidence and route stability can create a denial of service.", [
    `${ROOT}/experiments/dissertation_final_figures_v2/tables/sinkhole_defence_operational_cost.csv`,
    `${ROOT}/experiments/sinkhole_defence_v1/results_summary.md`
  ]);
}

// 19. LLM layer
{
  const s = pres.slides.add(); s.background.fill = C.white; title(s, "LLM layer: explanation after detection", "The language model is not the IDS and is not required for the empirical claims.", 19, "Interpretability");
  const x = [76, 352, 628, 904]; const h = ["IDS OUTPUT", "EVIDENCE", "EXPLANATION", "EVALUATION"];
  const b = ["label + confidence", "features + drift + trust", "structured analyst text", "faithfulness + errors"];
  for (let i = 0; i < 4; i++) {
    circle(s, x[i] + 72, 204, 72, i === 2 ? C.teal : C.navy, String(i + 1), 22);
    text(s, h[i], x[i], 304, 216, 28, 16, C.ink, true, "center");
    text(s, b[i], x[i], 346, 216, 62, 17, C.muted, false, "center");
    if (i < 3) text(s, ">", x[i] + 222, 224, 44, 46, 28, C.line, true, "center");
  }
  box(s, 114, 484, 1052, 96, C.soft, "none", 4);
  text(s, "Current status", 140, 500, 170, 26, 16, C.teal, true);
  text(s, "A local deterministic evidence-to-explanation-to-scoring pipeline is demonstrable. External LLM quality is not yet an evaluated dissertation result.", 140, 532, 980, 42, 19, C.ink, true);
  addNotes(s, "Timing: 21:40-22:35. The architecture keeps prediction and explanation separate. The IDS provides structured evidence. An LLM could translate that evidence for an analyst. The evaluation must test faithfulness to the supplied features and drift evidence, consistency and hallucination. For the live demo, show the deterministic local pipeline only and state clearly that it validates integration, not external LLM performance.", [
    `${ROOT}/experiments/llm_explanations_v2/README.md`,
    `${ROOT}/experiments/llm_explanations_v2/LIVE_DEMO_PLAN.md`
  ]);
}

// 20. Demo plan
{
  const s = pres.slides.add(); s.background.fill = C.white; title(s, "Live demonstration and fallback", "The demo is short, preloaded and backed by recorded evidence.", 20, "Demonstration");
  const rows = [
    ["COOJA LIVE", "4-5 min", "Open a validated Sybil run; show topology, 240 s activation and virtual-identity DIO markers."],
    ["LOCAL PIPELINE", "2 min", "Regenerate one structured explanation case and run the deterministic scoring script in VS Code terminal."],
    ["BACKUP VIDEO", "2-3 min shown", "Use short clips immediately if Cooja is slow. Never wait for a full simulation in front of the panel."]
  ];
  rows.forEach((r, i) => { const y = 166 + i * 124; text(s, r[0], 78, y, 190, 34, 18, [C.teal, C.blue, C.amber][i], true); text(s, r[1], 292, y, 130, 34, 18, C.ink, true); text(s, r[2], 452, y - 4, 720, 72, 19, C.muted, false); line(s, 78, y + 86, 1094, 1, C.line); });
  box(s, 78, 556, 1094, 62, C.navy, "none", 4);
  text(s, "Record four clips: control, blackhole, sinkhole and Sybil • 45-90 s each • 5-6 min prepared in total", 98, 568, 1054, 38, 19, C.white, true, "center");
  addNotes(s, "Timing: 22:35-29:00 including demos. Cooja: allow 30 seconds to open the preloaded configuration, 90 to 150 seconds to accelerate toward 240 simulated seconds, 90 seconds to inspect the marker and topology, then 30 seconds to summarise. Local explanation pipeline: 30 seconds to open evidence, 60 seconds to run fixture generation and scoring, 30 seconds to explain the boundary. Prepare four backup videos, each 45 to 90 seconds. Total recorded material is about five to six minutes, but show only two or three minutes if the live demo fails.", [
    `${ROOT}/experiments/presentation_demo_pack_v1/recording_checklist.md`,
    `${ROOT}/experiments/presentation_demo_pack_v1/five_minute_script.md`,
    `${ROOT}/experiments/llm_explanations_v2/LIVE_DEMO_PLAN.md`
  ]);
}

// 21. Close
{
  const s = pres.slides.add(); s.background.fill = C.navy;
  text(s, "What this dissertation establishes", 76, 76, 960, 54, 38, C.white, true);
  line(s, 76, 146, 90, 5, C.teal);
  const take = [
    "Static RPL IDS models generalise poorly across changed attack mechanisms.",
    "Whole-seed adaptation produces substantial recovery without row-level leakage.",
    "Sybil provides a distinct identity-based attack surface and a strong adaptation case.",
    "Robustness and defence failures show where the current evidence and policies remain incomplete."
  ];
  take.forEach((v, i) => { circle(s, 82, 196 + i * 94, 42, i === 2 ? C.teal : "#324B6D", String(i + 1), 16); text(s, v, 148, 186 + i * 94, 980, 64, 22, C.white, i === 2); });
  box(s, 76, 596, 1110, 2, "#46617F");
  text(s, "Questions", 76, 618, 250, 48, 29, "#A7E7E8", true);
  text(s, "Al-mizan Jamal", 884, 626, 300, 32, 17, "#C6D0DD", true, "right");
  addNotes(s, "Timing: 29:00-30:00. Close with the four claims. The most defensible contribution is not that every attack has been solved. It is that controlled simulation shows where generalisation fails, how much target data can recover it, why feature mechanism matters and how the Sybil extension tests identity-based drift. Invite questions.", [
    `${ROOT}/experiments/dissertation_results_summary_v1/results_summary.md`,
    `${ROOT}/experiments/dissertation_results_summary_v1/core_argument.md`
  ]);
}

async function main() {
  await fs.mkdir(`${BUILD}/rendered`, { recursive: true });
  for (const [index, slide] of pres.slides.items.entries()) {
    const stem = `slide-${String(index + 1).padStart(2, "0")}`;
    const png = await pres.export({ slide, format: "png", scale: 1 });
    await fs.writeFile(`${BUILD}/rendered/${stem}.png`, new Uint8Array(await png.arrayBuffer()));
    const layout = await slide.export({ format: "layout" });
    await fs.writeFile(`${BUILD}/rendered/${stem}.layout.json`, await layout.text());
  }
  const montage = await pres.export({ format: "webp", montage: true, scale: 1 });
  await fs.writeFile(`${BUILD}/deck-montage.webp`, new Uint8Array(await montage.arrayBuffer()));
  const pptx = await PresentationFile.exportPptx(pres);
  await pptx.save(OUT);
  console.log(`Wrote ${OUT}`);
}

main().catch((err) => { console.error(err); process.exitCode = 1; });
