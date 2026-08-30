# Gope Dataset and Paper Alignment Notes

Sources inspected:

- `Adversarial_RL-Based_IDS_for_Evolving_Data_Environment_in_6LoWPAN.pdf`
- `2013-Elsevier-SVELTE realtime ID in the IoT.pdf`
- Supplied dataset folder: `/Users/mizzy/Documents/Dissertation/Dissertation_Cooja_Work/DR P`

## Why This Matters

The supplied Gope paper is the closest baseline for the dissertation because it targets evolving IDS behaviour in 6LoWPAN/RPL networks and explicitly connects RPL routing attacks, incremental learning, concept-drift detection and adversarial reinforcement learning.

SVELTE is useful background because it is a lightweight real-time IDS for IoT/6LoWPAN/RPL and focuses attention on routing-aware evidence rather than only application traffic volume.

## Dataset Audit Result

The supplied `DR P` folder contains eight attack datasets with 768,811 total rows.

Seven files have 71 columns and a `TYPE` label:

- blackhole
- sinkhole
- increase rank
- DIO suppression
- DIS flooding
- grayhole
- wormhole

Worst Parent has 10,850 rows and 46 columns, but no `TYPE` label. It should be audited separately before using it in supervised baseline reproduction.

## Important Feature Implication

The supplied dataset contains routing-aware fields that are missing from the first Cooja ML features:

- `Source_Rank`
- `Parrent_Node`
- `Parents_Count`
- `Src_DIO_count`
- `Dst_DIO_count`
- `Src_DAO_count`
- `Dst_DAO_count`
- `Src_DIS_count`
- `Dst_DIS_count`
- `hop_count`
- `pkt_loss`
- `same_parent`

This directly explains the current Cooja result: coarse run-level and radio-volume features detect blackhole packet dropping, but they are weak for sinkhole rank manipulation. The next defensible feature milestone is to add Cooja-derived routing features that correspond to the Gope/SVELTE routing-aware view.

## Presentable Next Task

Build a first Gope baseline using the seven labelled 71-column datasets:

1. select shared numeric features;
2. exclude identifiers and direct leakage where needed;
3. split without random row leakage where possible;
4. train a simple baseline classifier;
5. report accuracy, precision, recall, F1, F2, false-positive rate and confusion matrix;
6. then compare which Gope feature families are missing from Cooja.

In parallel, improve Cooja extraction with routing-aware instrumentation or logs, especially parent/rank/DIO/DAO features, so the Cooja sinkhole experiment becomes more comparable to the supplied dataset.
