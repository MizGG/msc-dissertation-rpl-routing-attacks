import fs from "node:fs/promises";
import { readFileSync } from "node:fs";
import { Presentation, PresentationFile } from "@oai/artifact-tool";

const ROOT = "/Users/mizzy/Dissertation_Cooja_Work/rpl-dis-flood";
const BUILD = `${ROOT}/experiments/dissertation_presentation_v1/.build`;
const ASSET = `${BUILD}/assets`;
const OUT = `${ROOT}/experiments/dissertation_presentation_v1/Al-Mizaan_Jamal_Dissertation_Presentation_v2.pptx`;
const PAPER_ARCH = "/Users/mizzy/Desktop/Screenshot 2026-08-29 at 12.31.40.png";

const C = { ink:"#111827", sub:"#475569", line:"#CBD5E1", pale:"#F1F5F9", white:"#FFFFFF", teal:"#007C83", blue:"#1D4ED8", red:"#B42318", amber:"#B45309", green:"#047857", navy:"#0F2239", grey:"#64748B" };
const pres = Presentation.create({ slideSize:{width:1280,height:720} });

function rect(s,x,y,w,h,fill=C.white,line="none") { return s.shapes.add({geometry:"rect",position:{left:x,top:y,width:w,height:h},fill,line:{style:"solid",fill:line,width:line==="none"?0:1}}); }
function tx(s,v,x,y,w,h,size=19,color=C.ink,bold=false,align="left",font="Aptos") { const q=s.shapes.add({geometry:"textbox",position:{left:x,top:y,width:w,height:h},fill:"none",line:{style:"solid",fill:"none",width:0}}); q.text=v; q.text.style={fontFamily:font,fontSize:size,color,bold,alignment:align,verticalAlignment:"middle"}; return q; }
function rule(s,x,y,w,color=C.line,h=1){rect(s,x,y,w,h,color);}
function header(s,title,sub,n,section){ tx(s,`  ${title}`,60,34,1120,47,34,C.ink,true); if(sub) tx(s,`  ${sub}`,60,82,1130,34,16,C.sub); rule(s,60,125,1120,C.line); rect(s,60,124,72,3,C.teal); tx(s,section,60,687,260,16,10,C.grey); tx(s,`${String(n).padStart(2,"0")}  `,1140,687,60,16,10,C.grey,true,"right"); }
function notes(s,talk,sources=[]){ const src=sources.length?`\n\n[Sources]\n${sources.map(x=>`- ${x}`).join("\n")}\n[/Sources]`:""; s.speakerNotes.textFrame.setText(talk+src); s.speakerNotes.setVisible(true); }
function img(s,path,x,y,w,h,fit="contain",crop){ const type=path.toLowerCase().endsWith(".jpg")?"image/jpeg":"image/png"; return s.images.add({blob:readFileSync(path),contentType:type,alt:path.split("/").pop(),fit,position:{left:x,top:y,width:w,height:h},...(crop?{crop}:{})}); }
function label(s,v,x,y,w,color=C.teal){ rect(s,x,y,w,25,color); tx(s,v,x,y,w,25,12,C.white,true,"center"); }
function callout(s,v,x,y,w,h,color=C.pale,accent=C.teal,size=18){ rect(s,x,y,w,h,color); rect(s,x,y,5,h,accent); tx(s,v,x+18,y+9,w-30,h-18,size,C.ink,true); }
function table(s,x,y,widths,headers,rows,opts={}){
  const headH=34,rowH=opts.rowH||34,total=widths.reduce((a,b)=>a+b,0); rect(s,x,y,total,headH,C.navy);
  let cx=x; headers.forEach((h,i)=>{tx(s,h,cx+8,y,widths[i]-16,headH,13,C.white,true,opts.align?.[i]||"left");cx+=widths[i];});
  rows.forEach((r,ri)=>{const yy=y+headH+ri*rowH;rect(s,x,yy,total,rowH,ri%2?C.white:C.pale);let xx=x;r.forEach((v,i)=>{tx(s,String(v),xx+8,yy,widths[i]-16,rowH,opts.size||13,opts.colors?.[i]||C.ink,opts.boldCols?.includes(i)||false,opts.align?.[i]||"left",opts.fontCols?.includes(i)?"Courier New":"Aptos");xx+=widths[i];});});
  rect(s,x,y,total,headH+rows.length*rowH,"none",C.line);
}
function barChart(s,x,y,w,h,cats,series,max=1){
  const left=125,right=25,top=24,bottom=38,plotW=w-left-right,plotH=h-top-bottom,groupH=plotH/cats.length;
  for(let k=0;k<=4;k++){const xx=x+left+plotW*k/4;rule(s,xx,y+top,1,C.line,plotH);tx(s,(max*k/4).toFixed(max<=1?2:0),xx-25,y+h-bottom+5,50,18,11,C.grey,false,"center");}
  cats.forEach((c,i)=>{const gy=y+top+i*groupH;tx(s,c,x,gy,115,groupH,13,C.ink,false,"right");series.forEach((sr,j)=>{const bh=Math.min(14,(groupH-8)/series.length),yy=gy+4+j*(bh+3),bw=plotW*(sr.values[i]/max);rect(s,x+left,yy,bw,bh,sr.color);tx(s,sr.values[i].toFixed(sr.decimals??2),x+left+bw+5,yy-2,54,bh+4,11,sr.color,true);});});
  series.forEach((sr,i)=>{rect(s,x+left+i*160,y,12,12,sr.color);tx(s,sr.name,x+left+18+i*160,y-4,140,20,11,C.sub);});
}
function metric(s,x,y,w,v,l,color=C.teal){tx(s,v,x,y,w,48,36,color,true);tx(s,l,x,y+48,w,40,14,C.sub);}

// 1
{
 const s=pres.slides.add();s.background.fill=C.white;rect(s,0,0,1280,18,C.teal);tx(s,"ADAPTIVE INTRUSION DETECTION FOR EVOLVING RPL ATTACKS",70,86,1110,32,15,C.teal,true);tx(s,"Controlled concept drift, Sybil identity attacks\nand operationally grounded evaluation",70,140,1040,132,48,C.navy,true);rule(s,70,310,480,C.line,2);tx(s,"AL-MIZAAN JAMAL",70,345,520,42,25,C.ink,true);tx(s,"MSc Cybersecurity dissertation defence",70,392,520,30,18,C.sub);tx(s,"Contiki-NG • Cooja • cross-attack transfer • whole-seed adaptation",70,548,1050,30,19,C.sub);tx(s,"30-minute defence presentation",70,598,420,26,14,C.grey);notes(s,"0:00-0:30. Introduce the dissertation as an empirical study of IDS behaviour when RPL attack mechanisms evolve. State that the work combines controlled Cooja attack implementations, cross-attack evaluation, supervised adaptation, online detection, an identity-based Sybil extension and isolated adaptive-controller experiments.");
}

// 2
{
 const s=pres.slides.add();header(s,"Problem, evidence and contribution","The dissertation asks whether an IDS trained in one RPL attack environment remains reliable when the mechanism changes.",2,"Research framing");
 table(s,70,158,[210,360,470],["Element","Question","Evidence produced"],[
  ["Generalisation","Does a static IDS transfer to a different attack family?","9 × 9 cross-attack matrix; 72 off-diagonal train/test pairs"],
  ["Adaptation","How much target data recovers detection?","0-3 complete target seeds; held-out target-seed evaluation"],
  ["New surface","Does identity manipulation behave differently?","Sybil baseline, low/high-rate campaign, identity monitoring"],
  ["Online response","Can change be detected and acted upon?","CUSUM, DDM, incremental baselines, DQN/DDQN controllers"],
  ["Operational validity","Do conclusions survive environmental change?","Relocation, lossy radio, trust analysis and defence cost"]
 ],{rowH:68,size:15,boldCols:[0]});
 callout(s,"Central argument: adaptation helps only when the feature representation exposes the changed mechanism.",70,560,1040,70,C.pale,C.teal,20);notes(s,"0:30-1:35. This is the organising logic for the presentation. Emphasise that the contribution is not simply implementing attacks. It is the linked evidence chain from protocol implementation to drift failure, adaptation, online response and operational limitations.",[`${ROOT}/experiments/dissertation_results_summary_v1/core_argument.md`]);
}

// 3
{
 const s=pres.slides.add();header(s,"RPL security context","RPL creates a rank-based routing graph toward a root; attacks target forwarding, control, route choice or identity.",3,"Technical context");
 table(s,70,158,[190,270,250,330],["Security surface","Implemented attacks","Protocol behaviour changed","Expected observables"],[
  ["Forwarding","Blackhole, grayhole","Drop all or selected application packets","Delivery, retransmission and response volume"],
  ["Rank and route","Sinkhole, increase rank, worst parent, wormhole","Advertised rank, parent choice or radio path","Rank, parent churn and topology/radio evidence"],
  ["Control plane","DIS flood, DIO suppression","Increase or suppress RPL control messages","DIS/DIO rates and timing"],
  ["Identity","Sybil","Rotate IPv6 source identity in DIO traffic","Distinct identities, churn and consistency"]
 ],{rowH:82,size:15,boldCols:[0]});
 tx(s,"Why Cooja",70,550,150,28,18,C.teal,true);tx(s,"Executes Contiki-NG firmware logic, controls seed/topology/radio conditions, and preserves protocol-level logs. It provides simulator validity, not physical deployment validity.",220,542,890,54,17,C.ink);notes(s,"1:35-2:50. Give the second examiner a concise RPL explanation. The root is the destination, rank expresses relative position, DIO and DIS are control messages, and nodes select parents. Then connect each attack to the observable evidence used by the IDS.",[`${ROOT}/experiments/dissertation_results_summary_v1/attack_coverage_table.csv`]);
}

// 4
{
 const s=pres.slides.add();header(s,"Relationship to SVELTE and Gope et al.","The prior papers shaped the security signals and adaptation question, but the experimental implementations differ.",4,"Literature positioning");
 table(s,48,154,[150,260,250,260,250],["Study","Environment","Security scope","Adaptive method","Role in this dissertation"],[
  ["SVELTE (2013)","Contiki/Cooja","RPL-aware sinkhole and selective forwarding detection","Hybrid routing and intrusion evidence","Motivates protocol-specific features and Cooja validation"],
  ["Gope et al. (2022)","NetSim","Multiple evolving RPL/6LoWPAN attack profiles","Adversarial RL; DQN/DDQN; DDM","Motivates drift, adaptation and adversarial profile selection"],
  ["This work","Contiki-NG/Cooja","Nine validated attack families plus Sybil rate variation","Static transfer; whole-seed retraining; online and isolated RL studies","Controlled firmware-level extension with leakage-aware evaluation"]
 ],{rowH:116,size:15,boldCols:[0]});
 callout(s,"Claim boundary: extension and empirical comparison, not an exact reproduction of the NetSim ARL architecture.",70,562,1080,56,C.pale,C.amber,18);notes(s,"2:50-4:10. SVELTE motivates using RPL-aware routing evidence. Gope et al. motivates an evolving environment, change detection and adaptive defenders. Our design chooses Cooja and whole-seed experiments to expose firmware behaviour and reduce leakage. It does not claim that a CART or local controller replaces the paper's complete architecture.",["/Users/mizzy/Downloads/2013-Elsevier-SVELTE realtime ID in the IoT.pdf","/Users/mizzy/Documents/Dissertation/diss papers/Adversarial_RL-Based_IDS_for_Evolving_Data_Environment_in_6LoWPAN.pdf"]);
}

// 5
{
 const s=pres.slides.add();header(s,"NetSim versus Cooja","The choice changes what can be controlled, inspected and claimed.",5,"Method comparison");
 img(s,PAPER_ARCH,55,155,445,315,"cover",{left:.055,top:.12,right:.47,bottom:.31});
 table(s,535,155,[190,220,250],["Criterion","NetSim route","Cooja route"],[
  ["Scale and scenario design","Strong for network-level profiles","Smaller campaigns; detailed firmware execution"],
  ["Protocol implementation","Model configuration","Real Contiki-NG application and RPL hook code"],
  ["Inspection","Aggregate simulator evidence","Attack markers, routing logs and radio traces"],
  ["Reproducibility risk","Simulator and model configuration","Contiki version, Cooja configuration and build state"],
  ["Validity limit","Abstracted implementation behaviour","No physical radio/hardware deployment"]
 ],{rowH:76,size:14,boldCols:[0]});
 tx(s,"Gope et al. architecture",55,488,445,24,13,C.sub,true,"center");tx(s,"The methods are complementary. Cooja provides implementation fidelity; NetSim supports the paper's larger adaptive architecture.",55,538,1080,48,18,C.ink,true,"center");notes(s,"4:10-5:20. Explain the trade-off rather than presenting Cooja as universally better. The paper's NetSim approach is appropriate for adversarial RL profiles and large scenario control. Cooja is appropriate for demonstrating that the attack code, RPL hooks and logs execute in Contiki-NG.",["/Users/mizzy/Documents/Dissertation/diss papers/Adversarial_RL-Based_IDS_for_Evolving_Data_Environment_in_6LoWPAN.pdf",`${ROOT}/experiments/dissertation_overleaf_v1/chapters/03_methodology.tex`]);
}

// 6
{
 const s=pres.slides.add();header(s,"Experimental protocol","Each family uses matched attack/control seeds and a delayed activation point.",6,"Methodology");
 table(s,70,160,[270,300,470],["Parameter","Value","Purpose"],[
  ["Topology","16 nodes; attack node 16 in baseline","Comparable routing environment across families"],
  ["Simulation duration","540 simulated seconds","Captures pre-attack and post-attack behaviour"],
  ["Attack activation","240 seconds","Separates normal warm-up from attack period"],
  ["Seeds","123456, 234567, 345678, 456789, 567890","Five independent matched repetitions"],
  ["Per-family baseline","5 attack + 5 control runs","Balanced condition-level validation"],
  ["Feature window","60 seconds","Temporal observations for drift and adaptation"],
  ["Split unit","Complete simulation seed/run","Prevents windows from one run crossing train and test"]
 ],{rowH:54,size:15,boldCols:[0]});
 notes(s,"5:20-6:25. Explain the activation and matched-control structure. Highlight that the split unit is the entire simulation seed. Randomly splitting rows would leak temporally related windows from the same run and inflate performance.",[`${ROOT}/experiments/final_simulated_dataset_v1/evaluation_protocol.md`]);
}

// 7
{
 const s=pres.slides.add();header(s,"Attack implementation and validation evidence","Ninety baseline Cooja runs were validated before any cross-attack IDS claim was made.",7,"Implementation validation");
 table(s,38,148,[150,200,105,110,360,250],["Attack","Mechanism","Attack","Control","Observed attack evidence","Status"],[
  ["Blackhole","Drop forwarding","5","5","Post-activation responses suppressed to 0-3","Validated"],
  ["Sinkhole","Advertise minimum rank","5","5","1 advertised-rank event per attack run","Validated"],
  ["DIS flood","Flood DIS","5","5","149 effect events per run","Validated"],
  ["Grayhole","Selective drop","5","5","208-211 effect events per run","Validated"],
  ["Increase rank","Degrade advertised rank","5","5","1-2 effect events per run","Validated"],
  ["DIO suppression","Suppress DIO","5","5","1-2 effect events per run","Validated"],
  ["Worst parent","Malicious parent choice","5","5","2630-3593 effect events per run","Validated"],
  ["Wormhole","Directed radio tunnel","5","5","1706-1725 tunnel events per run","Validated"],
  ["Sybil","Rotate DIO identity","5","5","150-151 spoofed identity events per run","Validated"]
 ],{rowH:48,size:13,boldCols:[0],align:["left","left","center","center","left","center"]});
 tx(s,"Baseline total: 45 attack + 45 matched control simulations",70,628,1060,28,18,C.teal,true,"center");notes(s,"6:25-7:30. This is the validation evidence behind the attack-coverage claim. Do not spend equal time on every row. Point out the different evidence mechanisms, then emphasise that Sybil produces direct virtual-identity DIO markers while controls produce none.",[`${ROOT}/experiments/dissertation_results_summary_v1/attack_coverage_table.csv`]);
}

// 8
{
 const s=pres.slides.add();header(s,"Frozen dataset and provenance controls","The dataset is generated from validated runs and keeps validation metadata separate from predictive evidence.",8,"Dataset construction");
 metric(s,70,165,220,"810","60-second windows",C.teal);metric(s,330,165,220,"90","run groups",C.blue);metric(s,590,165,220,"84","total columns",C.ink);metric(s,850,165,220,"57","generic predictive features",C.green);
 table(s,70,300,[230,300,510],["Column group","Included in model?","Examples and purpose"],[
  ["Predictive network features","Yes","Delivery, radio, routing-state, parent and identity evidence"],
  ["Run provenance","No","Family, seed, attack/control mode and source file"],
  ["Attack markers","No","Ground-truth activation and mechanism validation"],
  ["Labels","Target only","Normal versus post-activation attack windows"]
 ],{rowH:62,size:15,boldCols:[0]});
 callout(s,"Sixteen marker/provenance fields are excluded from predictors. Whole-seed grouping is retained through every evaluation.",70,570,1040,60,C.pale,C.red,18);notes(s,"7:30-8:35. The frozen dataset contains 810 windows across 90 baseline run groups. Explain that provenance is necessary for auditability but cannot be a predictive shortcut. Attack markers identify activation and validate the implementation, but they are not features.",[`${ROOT}/experiments/final_simulated_dataset_v1/evaluation_protocol.md`,`${ROOT}/experiments/final_simulated_dataset_v1`]);
}

// 9
{
 const s=pres.slides.add();header(s,"IDS evaluation stack","Different models answer different questions; they are not treated as interchangeable.",9,"Models");
 table(s,60,154,[180,280,240,360],["Component","Models","Evaluation mode","Question answered"],[
  ["Static baseline","CART; Gaussian","Cross-family train/test transfer","Does a fixed representation generalise?"],
  ["Supervised adaptation","CART + 0-3 target seeds","Held-out whole target seeds","How much labelled target data restores performance?"],
  ["Online baselines","Gaussian update; River NB; Hoeffding tree","Prequential stream evaluation","Can incremental learning respond without batch retraining?"],
  ["Change detection","CUSUM; DDM","Held-out post-activation stream","When should adaptation be triggered?"],
  ["Adaptive controller","DQN and DDQN","Isolated held-out Sybil stream","Can a learned policy choose adaptation actions?"],
  ["Identity monitor","Rule-based consistency signal","Post-activation Sybil/control windows","Does an identity-specific observable expose Sybil directly?"]
 ],{rowH:74,size:15,boldCols:[0]});
 notes(s,"8:35-9:45. Distinguish the main dissertation result from the isolated adaptive package. CART cross-attack and whole-seed adaptation are the strongest broad evidence. The online and DQN/DDQN experiments are narrower Sybil-focused extensions and must be reported with that boundary.",[`${ROOT}/experiments/adversarial_rl_sybil_v1/README.md`,`${ROOT}/experiments/dissertation_results_summary_v1/results_summary.md`]);
}

// 10
{
 const s=pres.slides.add();header(s,"Static cross-attack transfer matrix","CART is trained on one attack/control environment and evaluated on a different held-out family.",10,"Concept drift result");img(s,`${ASSET}/cross_attack_cart_f1_heatmap.png`,70,145,840,505);metric(s,940,176,240,"48 / 72","cross-attack pairs with zero recall",C.red);metric(s,940,330,240,"6 / 72","pairs with F1 ≥ 0.80",C.green);metric(s,940,484,240,"0.182","mean cross-attack F1",C.teal);notes(s,"9:45-11:15. Show how to read one cell. Rows are source attack families and columns are different target families. Forty-eight of 72 off-diagonal CART pairings miss every attack window. Only six reach F1 at least 0.8. This is controlled attack-distribution drift rather than naturally observed field drift.",[`${ROOT}/experiments/dissertation_final_figures_v2/tables/cross_attack_cart_f1.csv`,`${ROOT}/experiments/dissertation_results_summary_v1/concept_drift_key_metrics.csv`]);
}

// 11
{
 const s=pres.slides.add();header(s,"Static models agree on the failure, not its severity","The weaker Gaussian baseline shows that model choice does not remove the representation problem.",11,"Model comparison");
 barChart(s,70,170,760,380,["Mean recall","Mean F1","Strong F1 pairs / 72"],[{name:"CART",values:[.2333,.1822,6/72],color:C.teal},{name:"Gaussian",values:[.0739,.0362,0],color:C.red}],1);
 table(s,860,180,[160,155],["Metric","Result"],[
  ["CART zero recall","48 / 72"],["Gaussian zero recall","66 / 72"],["CART mean F1","0.1822"],["Gaussian mean F1","0.0362"],["Interpretation","failure persists"]
 ],{rowH:58,size:15,boldCols:[0]});
 callout(s,"Accuracy alone is misleading on windowed data because pre-attack and control windows dominate the normal class.",70,584,1070,56,C.pale,C.amber,17);notes(s,"11:15-12:15. CART is stronger than Gaussian, but both transfer poorly. Explain why recall and F1 matter more than accuracy: a model can predict normal for every row and still obtain apparently acceptable accuracy when normal windows dominate.",[`${ROOT}/experiments/dissertation_results_summary_v1/concept_drift_key_metrics.csv`]);
}

// 12
{
 const s=pres.slides.add();header(s,"Feature representation changed the sinkhole conclusion","The early coarse result failed; routing-state evidence made supervised adaptation possible.",12,"Feature ablation");
 table(s,70,158,[260,180,150,150,300],["Blackhole → sinkhole condition","Seeds","Recall","F1","Interpretation"],[
  ["Static coarse windows","0","0.000","0.000","All attack windows missed"],
  ["Coarse adaptation","3","0.060","0.098","Retraining still lacks rank evidence"],
  ["Routing-aware adaptation","1","0.730","0.813","Low-rank advertisement becomes learnable"],
  ["Routing-aware adaptation","2","0.873","0.909","Further recovery"],
  ["Routing-aware adaptation","3","0.950","0.973","High recall with FPR 0"]
 ],{rowH:68,size:16,boldCols:[0]});
 callout(s,"Failure analysis changed the method: the representation was extended before making a general adaptation claim.",70,548,1040,76,C.pale,C.teal,20);notes(s,"12:15-13:35. This is a central methodological learning. The original blackhole-to-sinkhole experiment produced zero recall. Simply adding sinkhole examples to coarse traffic features did not solve it. Once persistent advertised-rank and routing-state evidence was included, one to three whole target seeds produced F1 from 0.813 to 0.973. This directly supports the feature-plus-adaptation argument.",[`${ROOT}/experiments/results/master_results_summary.csv`,`${ROOT}/experiments/routing_features_v1/results/RESULTS_INTERPRETATION.md`]);
}

// 13
{
 const s=pres.slides.add();header(s,"Whole-seed adaptation curve across nine families","Target-family runs are added to training, while evaluation remains on unseen target seeds.",13,"Adaptation result");img(s,`${ASSET}/overall_adaptation_curve.png`,70,150,800,470);table(s,890,170,[90,80,80,80],["Seeds","Recall","F1","FPR"],[
  ["0","0.233","0.182","0.112"],["1","0.806","0.826","0.021"],["2","0.862","0.866","0.027"],["3","0.892","0.879","0.030"]
 ],{rowH:68,size:14,align:["center","center","center","center"],boldCols:[0]});tx(s,"Largest recovery occurs after the first complete target seed.",890,495,330,64,17,C.teal,true,"center");notes(s,"13:35-14:55. The overall mean F1 rises from 0.1822 to 0.8258 after one target seed, then to 0.8792 after three. Point out the small FPR increase after additional seeds. The curve supports rapid supervised recovery on average, but the next slide shows that family-specific outcomes are not monotonic.",[`${ROOT}/experiments/dissertation_results_summary_v1/adaptation_key_metrics.csv`]);
}

// 14
{
 const s=pres.slides.add();header(s,"Adaptation is heterogeneous across attack pairs","Mean recovery does not imply every source-target pairing improves monotonically.",14,"Adaptation detail");
 table(s,58,154,[210,170,140,140,140,260],["Source → target","Static F1","1 seed","2 seeds","3 seeds","Observed pattern"],[
  ["Blackhole → DIS flood","0.000","1.000","1.000","1.000","Immediate clean recovery"],
  ["Blackhole → sinkhole","0.000","0.571","0.966","0.947","Two seeds outperform one and three"],
  ["Blackhole → wormhole","0.000","0.778","0.692","0.727","Non-monotonic"],
  ["DIO suppression → Sybil","0.000","0.889","0.846","0.750","More target data reduces this pairing"],
  ["DIS flood → DIO suppression","0.000","0.000","0.000","0.000","Representation remains insufficient"],
  ["Grayhole → blackhole","1.000","1.000","1.000","1.000","Mechanism similarity transfers"]
 ],{rowH:68,size:15,boldCols:[0]});
 callout(s,"The correct claim is average recovery with unresolved pair-specific failures, not universal convergence.",70,598,1040,48,C.pale,C.red,17);notes(s,"14:55-16:10. Use this table to avoid overclaiming the overall adaptation curve. Some pairs recover immediately, some are non-monotonic, and DIS flood to DIO suppression remains undetected despite target examples. This points to limited samples, model instability and missing mechanism-specific evidence.",[`${ROOT}/experiments/cross_attack_adaptation_with_sybil_v1/cross_attack_adaptation_summary.csv`]);
}

// 15
{
 const s=pres.slides.add();header(s,"Why Sybil is a meaningful new attack surface","One physical node creates multiple apparent RPL identities, changing the observable from forwarding or rank to identity consistency.",15,"Sybil contribution");
 table(s,58,154,[210,230,275,330],["Dimension","Existing attack examples","Sybil mechanism","Why it matters for drift"],[
  ["Primary surface","Packet forwarding; rank; control rate","IPv6 source identity in outgoing DIO messages","Out-of-family representation shift"],
  ["Trust implication","One neighbour accumulates history","Each virtual identity can appear new","Forwarding-only trust can be reset or diluted"],
  ["Implementation","Shared flag and delayed activation","Rotating virtual source identities after 240 s","Direct protocol marker and rate control"],
  ["Baseline evidence","Family-specific attack markers","150-151 spoofed DIO markers per run","Five attacks positive; five controls zero"],
  ["Novelty boundary","Known Sybil concept","New implementation/evaluation within this project","Not claimed as invention of Sybil itself"]
 ],{rowH:78,size:15,boldCols:[0]});
 callout(s,"Contribution: a new identity-manipulation attack surface in the dissertation's controlled Cooja and adaptation framework.",70,582,1040,56,C.pale,C.blue,18);notes(s,"16:10-17:30. Give the detailed explanation. Sybil is selected because it is mechanism-distinct, not because it is simply an additional attack. It challenges identity continuity and trust bootstrapping, supplies an out-of-family drift target, and supports rate variation. The novelty claim is the implementation and evaluation in this framework, not invention of the Sybil attack.",[`${ROOT}/experiments/sybil_attack_v1/README.md`,`${ROOT}/experiments/dissertation_results_summary_v1/sybil_contribution_summary.md`]);
}

// 16
{
 const s=pres.slides.add();header(s,"Sybil rate campaign: sensitivity beyond one attack setting","Five seeds were run for low rate, high rate and matched control conditions.",16,"Sybil experiment");
 table(s,70,156,[210,150,170,190,260],["Condition","Runs","Spoofed DIO / run","Node 16 TX after 240 s","Total radio TX, mean"],[
  ["Control","5","0","1,676-1,699","8,984"],
  ["Low-rate Sybil","5","29","1,707-1,736","9,020"],
  ["High-rate Sybil","5","299","1,986-1,997","9,301"]
 ],{rowH:90,size:17,boldCols:[0],align:["left","center","center","center","center"]});
 barChart(s,100,470,980,150,["Control","Low rate","High rate"],[{name:"Spoofed DIO markers",values:[0,29,299],color:C.blue,decimals:0}],320);
 callout(s,"Higher attack rate is directly observable, but it also changes radio load and may be easier to detect.",70,610,1040,44,C.pale,C.amber,16);notes(s,"17:30-18:35. The low-rate profile sends 29 spoofed identity markers, while the high-rate profile sends 299. High rate also increases node 16 and total radio transmissions. This creates a useful adversarial trade-off: aggressive behaviour has greater impact but a stronger signature.",[`${ROOT}/experiments/adversarial_rl_sybil_v1/results/sybil_rate_campaign_metrics.csv`]);
}

// 17
{
 const s=pres.slides.add();header(s,"Sybil detection and adaptation evidence","Identity-specific evidence is strong; generic cross-attack transfer remains weak without target data.",17,"Sybil result");
 table(s,60,158,[270,160,160,160,280],["Evaluation","Precision","Recall","F1","Interpretation"],[
  ["Sybil target, static CART","0.216","0.275","0.218","Poor cross-family transfer"],
  ["Sybil target, 1 seed","1.000","0.944","0.968","Large held-out recovery"],
  ["Sybil target, 3 seeds","1.000","0.950","0.969","Stable high performance"],
  ["Identity monitor, attack","1.000","1.000","1.000","50/50 post-activation windows alerted"],
  ["Identity monitor, control","n/a","n/a","n/a","0/45 control windows alerted"]
 ],{rowH:68,size:16,boldCols:[0]});
 metric(s,70,558,280,"11 / 16","Sybil-related static pairs with zero recall",C.red);metric(s,410,558,280,"0.968","F1 after one complete Sybil seed",C.teal);metric(s,750,558,340,"50 / 50","identity-monitor attack windows alerted",C.blue);notes(s,"18:35-19:50. Separate the generic IDS and identity monitor. Static models involving Sybil have 11 zero-recall failures out of 16 pairings. Supervised adaptation recovers strongly. The identity-specific monitor detects all 50 post-activation windows with zero alerts in 45 controls, but this is a rule-based mechanism-specific result on a small controlled campaign.",[`${ROOT}/experiments/dissertation_results_summary_v1/adaptation_key_metrics.csv`,`${ROOT}/experiments/adversarial_rl_sybil_v1/results/sybil_identity_monitor_summary.csv`]);
}

// 18
{
 const s=pres.slides.add();header(s,"Adaptive-controller extension: useful but not yet superior","The isolated DQN/DDQN experiment tests policy-controlled updating on 72 held-out Sybil stream windows.",18,"Adaptive IDS extension");
 table(s,70,158,[260,150,150,150,150,220],["Policy / algorithm","Accuracy","Precision","Recall","F1","Finding"],[
  ["Static source / DQN","0.722","0.000","0.000","0.000","All 20 attacks missed"],
  ["Always incremental / DQN","0.861","1.000","0.500","0.667","Best DQN policy"],
  ["RL controller / DQN","0.778","1.000","0.200","0.333","Under-updates"],
  ["Static source / DDQN","0.722","0.000","0.000","0.000","All 20 attacks missed"],
  ["Always incremental / DDQN","0.861","1.000","0.500","0.667","Best DDQN policy"],
  ["RL controller / DDQN","0.833","1.000","0.400","0.571","Improves on DQN controller"]
 ],{rowH:60,size:15,boldCols:[0]});
 callout(s,"The learned controller does not beat always-incremental updating. This is an extension result and a limitation, not evidence of RL superiority.",70,576,1040,64,C.pale,C.red,18);notes(s,"19:50-21:05. This slide corrects the omission in the first deck. The DQN and DDQN controllers were implemented locally and evaluated on a held-out Sybil stream. DDQN improves over the DQN controller, but both remain below always-incremental updating. The result is scientifically useful because it prevents an unjustified claim that RL automatically improves adaptation.",[`${ROOT}/experiments/adversarial_rl_sybil_v1/results/adversarial_rl/held_out_summary.csv`,`${ROOT}/experiments/adversarial_rl_sybil_v1/docs/model_scope.md`]);
}

// 19
{
 const s=pres.slides.add();header(s,"Online drift detection: trigger timing matters","Mechanism-aware CUSUM reacts earlier than delayed classifier-error monitoring.",19,"Online response");img(s,`${ASSET}/online_drift_detection.png`,65,150,820,475);table(s,915,176,[145,120],["Detector","Result"],[
  ["CUSUM attack","5 / 5"],["CUSUM control","0 / 5 alerts"],["CUSUM delay","0 s window"],["DDM attack","5 / 5"],["DDM control","0 / 5 alerts"],["DDM delay","60 s"]
 ],{rowH:54,size:15,boldCols:[0]});tx(s,"Five-seed controlled result",915,535,265,30,16,C.amber,true,"center");notes(s,"21:05-22:00. CUSUM operates on the rank-state signal and alerts in the first post-activation window. DDM waits for delayed classifier errors and alerts one 60-second window later. The sample is five attack and five matched control runs, so the zero false-alert rate is not a field estimate.",[`${ROOT}/experiments/online_drift_response_v1/results/detector_comparison_summary.csv`]);
}

// 20
{
 const s=pres.slides.add();header(s,"Robustness under attacker relocation and lossy radio","Sixty additional runs test whether adaptation depends on the baseline position and radio model.",20,"Robustness");img(s,`${ASSET}/robustness_static_vs_adapted_f1.png`,60,150,850,470);table(s,935,175,[145,120],["Condition","3-seed F1"],[
  ["BH relocated","1.000"],["SH relocated","1.000"],["Sybil relocated","0.995"],["BH lossy","1.000"],["SH lossy","1.000"],["Sybil lossy","0.937"]
 ],{rowH:57,size:15,boldCols:[0]});tx(s,"Lossy Sybil FPR = 0.046",935,550,265,44,16,C.red,true,"center");notes(s,"22:00-23:00. Three-seed adaptation remains high under relocation and lossy radio. Lossy-radio Sybil is the weakest case at F1 0.9367 and FPR 0.0462. This supports limited simulator robustness, not physical deployment generalisation.",[`${ROOT}/experiments/dissertation_final_figures_v2/tables/robustness_static_vs_adapted.csv`]);
}

// 21
{
 const s=pres.slides.add();header(s,"Trust features and active defence produced negative results","Interpretability improved, but predictive metrics and network operation did not.",21,"Trust and defence");
 table(s,55,158,[270,150,150,150],["Trust-layer evaluation","Baseline F1","Trust F1","Change"],[
  ["Static cross-attack","0.1822","0.1822","0.0000"],["1-seed adaptation","0.8258","0.8258","0.0000"],["2-seed adaptation","0.8664","0.8664","0.0000"],["3-seed adaptation","0.8792","0.8792","0.0000"]
 ],{rowH:58,size:15,boldCols:[0]});
 table(s,730,158,[210,150,150],["Sinkhole condition","App responses","Radio TX"],[
  ["Control","417.4","5,217"],["Attack","416.6","5,243"],["Rank-parent defence","87.4","35,020"]
 ],{rowH:58,size:15,boldCols:[0]});
 callout(s,"Trust: diagnostic evidence only; no predictive gain.",55,462,620,62,C.pale,C.teal,18);callout(s,"Defence: −79.1% responses, +571.2% radio TX, 681.8 parent switches.",730,462,495,82,C.pale,C.red,18);
 tx(s,"Lesson: detection confidence, hysteresis and route-stability constraints are required before routing intervention.",70,584,1080,40,18,C.ink,true,"center");notes(s,"23:00-24:10. The trust features did not change any measured static or adaptation F1 values. The active sinkhole policy was operationally harmful: responses collapsed, transmissions rose and routes churned. Present both as negative results that improve the dissertation by establishing where the proposed ideas fail.",[`${ROOT}/experiments/trust_layer_v1/results/trust_vs_baseline_comparison.csv`,`${ROOT}/experiments/operational_overhead_v1/operational_overhead_table.csv`]);
}

// 22
{
 const s=pres.slides.add();header(s,"External Gope data shows the same transfer failure","The supplied data provides a preliminary comparison, but its row-level structure limits equivalence.",22,"External validation");
 table(s,55,158,[300,150,150,150,150,250],["Experiment","Accuracy","Precision","Recall","F1","Validity note"],[
  ["All labelled attacks, routing Gaussian","0.622","0.864","0.266","0.407","Random row holdout; high precision, low recall"],
  ["Blackhole → sinkhole transfer","0.508","0.607","0.047","0.088","Attack files separated; weak cross-attack transfer"]
 ],{rowH:98,size:16,boldCols:[0]});
 barChart(s,90,420,1000,170,["Cooja CART BH→SH","Gope Gaussian BH→SH"],[{name:"Recall",values:[0,.0472],color:C.red},{name:"F1",values:[0,.0876],color:C.teal}],.12);
 callout(s,"Comparable direction, not directly comparable magnitude: simulator, features, labels and split units differ.",70,600,1040,48,C.pale,C.amber,17);notes(s,"24:10-25:15. The external supplied dataset reproduces the direction of failure: blackhole to sinkhole recall is 0.0472 and F1 0.0876. Do not compare the magnitude directly with Cooja because the data generators, feature schemas and row grouping differ. The all-attack baseline also has high precision but low recall.",[`${ROOT}/experiments/gope_dataset/gope_baseline_results.csv`,`${ROOT}/experiments/gope_dataset/paper_alignment.md`]);
}

// 23
{
 const s=pres.slides.add();header(s,"What failed, and how the work improved","The dissertation records methodological corrections instead of hiding unsuccessful experiments.",23,"Critical reflection");
 table(s,60,154,[250,310,350,260],["Failure","Diagnosis","Correction made","Residual limitation"],[
  ["BH → sinkhole adaptation failed","Coarse traffic features did not expose rank manipulation","Added rank, parent and routing-state features","Some family pairs still fail"],
  ["Random-row evaluation risk","Windows from one run can leak across splits","Grouped all evaluation by complete seed/run","Only five baseline seeds"],
  ["Trust added no F1 gain","Signals duplicated existing routing evidence","Reframed trust as an explanation layer","No stable trust-based prevention"],
  ["Sinkhole defence caused churn","Hard rejection lacked stability controls","Reported operational cost and derived design requirements","No successful defence campaign yet"],
  ["RL controller underperformed","Small stream and weak reward/action policy","Compared against always-incremental baseline","No demonstrated RL superiority"]
 ],{rowH:84,size:15,boldCols:[0]});notes(s,"25:15-26:25. This slide demonstrates ownership of the research. Walk through the early sinkhole failure, leakage correction, trust result, defence instability and RL underperformance. Each failure changed either the method, the claim or the future design.",[`${ROOT}/experiments/dissertation_overleaf_v1/chapters/06_discussion.tex`,`${ROOT}/experiments/dissertation_overleaf_v1/chapters/07_limitations.tex`]);
}

// 24
{
 const s=pres.slides.add();header(s,"Live demonstration and recorded fallback","The defence presentation should demonstrate evidence, not wait for long simulations.",24,"Demonstration");
 table(s,60,154,[190,130,470,310],["Segment","Time","Live action","Fallback"],[
  ["Cooja Sybil","4-5 min","Open validated configuration; accelerate to 240 s; show identity markers and topology","60-90 s recorded Sybil clip"],
  ["Evidence files","1 min","Open validation summary and one COOJA.testlog","Static screenshots/log extract"],
  ["Local adaptive pipeline","2 min","Run deterministic evidence package and scoring; optionally show held-out RL table","Prepared terminal output"],
  ["Transition","30 s","Return to conclusion slide","None"]
 ],{rowH:86,size:16,boldCols:[0]});
 tx(s,"Record four clips before the defence",70,548,360,28,18,C.teal,true);tx(s,"Control • blackhole • sinkhole • Sybil",440,548,620,28,18,C.ink,true);tx(s,"45-90 seconds each; prepare 5-6 minutes total, show only the relevant 2-3 minutes if live Cooja fails.",70,590,1040,44,17,C.sub);notes(s,"26:25-29:15 including live demonstration. Preload the Cooja configuration before presenting. Do not wait for a complete simulation. The local adaptive demo must not be described as an external LLM result. If anything stalls, switch immediately to the recorded clip and preserved result table.",[`${ROOT}/experiments/presentation_demo_pack_v1/recording_checklist.md`,`${ROOT}/experiments/llm_explanations_v2/LIVE_DEMO_PLAN.md`]);
}

// 25
{
 const s=pres.slides.add();s.background.fill=C.navy;rect(s,0,0,1280,14,C.teal);tx(s,"CONCLUSIONS",70,66,200,26,14,"#7DD3D6",true);tx(s,"What the evidence supports",70,108,960,52,39,C.white,true);
 table(s,70,198,[200,860],["Evidence","Defensible conclusion"],[
  ["Static transfer","RPL IDS performance is brittle under controlled cross-attack distribution change."],
  ["Adaptation","One complete target seed produces the largest average recovery, but pair-specific failures remain."],
  ["Representation","Mechanism-aware rank, parent, control and identity features determine whether adaptation can work."],
  ["Sybil","Identity manipulation is a distinct new surface in this framework and is strongly learnable after limited adaptation."],
  ["Online and RL","Change detection and adaptive controllers are feasible, but the current RL controller does not outperform simple incremental updating."],
  ["Operational limits","Trust and defence experiments show that detection accuracy alone is insufficient for safe routing intervention."]
 ],{rowH:62,size:16,boldCols:[0]});
 tx(s,"Questions",70,618,300,42,28,"#9FE3E5",true);tx(s,"AL-MIZAAN JAMAL",900,626,300,28,16,"#CBD5E1",true,"right");notes(s,"29:15-30:00. Close by stating exactly what the evidence supports. The strongest claim is a linked one: cross-attack drift causes failure, mechanism-aware evidence enables adaptation, Sybil extends the identity surface, and operational experiments show why adaptation and defence must be evaluated beyond accuracy.",[`${ROOT}/experiments/dissertation_results_summary_v1/results_summary.md`]);
}

async function main(){await fs.mkdir(`${BUILD}/v2_rendered`,{recursive:true});for(const [i,s] of pres.slides.items.entries()){const png=await pres.export({slide:s,format:"png",scale:1});await fs.writeFile(`${BUILD}/v2_rendered/slide-${String(i+1).padStart(2,"0")}.png`,new Uint8Array(await png.arrayBuffer()));}const pptx=await PresentationFile.exportPptx(pres);await pptx.save(OUT);console.log(`Wrote ${OUT}`);}
main().catch(e=>{console.error(e);process.exitCode=1;});
