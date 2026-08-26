# Submission Checklist

## Must Finish

- Move the text from `final_dissertation_draft.md` into the university
  dissertation template.
- Add proper citations for RPL, Contiki-NG/Cooja, concept drift, IDS evaluation,
  the Gope/professor dataset and trust-based RPL defences.
- Insert the four final SVG figures or export them to PDF/PNG if the template
  requires raster images.
- Insert the key CSV tables as formatted dissertation tables.
- Check that every reported number matches the preserved CSV evidence.
- Add appendix links or descriptions for the experiment folders.
- Proofread for tense, formatting, references and figure numbering.

## Claims To Keep

- Static IDS models generalise poorly under controlled cross-attack drift.
- Whole-seed adaptation substantially improves held-out target-family
  detection.
- Sybil is the main new attack-surface contribution.
- Feature representation matters: adaptation only helps when the changed
  mechanism is visible in the extracted features.
- Trust diagnostics improve interpretation but are not a complete online
  defence.
- The LLM layer, if included later, explains evidence and is not the IDS.

## Claims To Avoid

- Do not claim the IDS solves concept drift.
- Do not claim the trust layer prevents all attacks.
- Do not claim the Sybil experiment proves cryptographic identity compromise.
- Do not claim deterministic LLM fixture outputs are live LLM performance.
- Do not claim Cooja results prove deployment robustness on physical IoT
  hardware.

## Presentation Prep

- Record short Cooja clips for blackhole, sinkhole, Sybil and one control run.
- Keep the live demo focused on VS Code, Terminal and preserved results.
- Avoid running full Cooja batches live during the presentation.
- Use `experiments/presentation_demo_pack_v1/five_minute_script.md` as the
  speaking route.
