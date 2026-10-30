# Artifact contract

The run has one owner and one canonical file for each kind of decision.

| Artifact | Owner | Purpose | Consumers |
|---|---|---|---|
| `reference_videos/<reference-id>/source.*` | `hypit` | Downloaded source with preserved timing | reference analysis |
| `reference_videos/<reference-id>/transcript.json` | local ASR | Timed speech evidence | reference analysis, script adaptation |
| `reference_videos/<reference-id>/boundaries.json` and `frames/` | `hypit` | Candidate cuts and visual evidence | reference analysis |
| `reference_videos/<reference-id>/reference_analysis.json` | pipeline reference branch | Shot-by-shot audiovisual blueprint | variant allocation, shot planning |
| `variants/<variant-id>/reference_plan.json` | model reference router | Minimal selected reference set for the chosen backend and reasons | model prompt and submission |
| `product_manifest.json` | `product-ugc-pipeline` | Complete source asset inventory and provenance | all later stages |
| `image_analysis.json` | `product-ugc-pipeline` | Observation of every manifest image | product brief, reference selection |
| `product_brief.json` | `product-ugc-pipeline` | Verified product facts, mechanics and unknowns | shot planning, prompts, QC |
| `product_reference_set/` | `product-ugc-pipeline` | Canonical identity images plus hashes and roles | storyboard, selected backend, QC |
| `shot_rows.json` | `commerce-production-workflow` populated by `commerce-shot-grammar` | One timeline, blocking, camera and product state plan | storyboard, previs, prompt draft |
| `storyboard.png` | `commerce-production-workflow` | Chronological visual plan | prompt draft, selected backend references, QC |
| `previs.png` | `commerce-production-workflow` | Spatial/action geometry plan | prompt draft, QC |
| `action_prompt_draft.md` | `writing-video-prompts` | Model-neutral motion, physics and sound draft | selected backend adapter |
| `model_prompt.md` | selected backend adapter (`minimax-h3-creative-director` for H3 or this skill’s Omni formatter) | The one final prompt/envelope for the selected backend, with source structure and replacement ledger | submission |
| `submission_manifest.json` | `ad-muse` | Paid task, cost, result, download and QC state | delivery and recovery |
| `qc/technical.json` | pipeline QC | File/playback validation | delivery |
| `qc/creative.json` | pipeline QC | Sampled visual/audio/product validation | delivery |

`commerce-shot-grammar` does not create a second storyboard or a second previs when the outer workflow already owns those files. It writes its decisions into `shot_rows.json` and the outer workflow records the artifact paths.

`writing-video-prompts` does not create the final model prompt. Its output is an advisory action draft that can be replaced by a corrected draft before backend formatting.

`model_prompt.md` is the only paid-generation prompt. Submission scripts must read that file and the reference list recorded beside it; they must not reconstruct a prompt from a summary.

## State transitions

```text
intake_pending
→ intake_passed
→ shot_plan_passed
→ required_reference_qc_passed
→ action_draft_passed
→ model_prompt_passed
→ ready_to_submit
→ submitted
→ remote_final
→ downloaded
→ technical_qc_passed
→ creative_qc_passed | needs_review | failed
```

If an upstream artifact changes, invalidate its downstream artifacts by revision/hash. Do not silently reuse a stale storyboard, prompt or submission manifest.

Identity images, storyboard and previs are conditional. When omitted by the reference plan, record `not_required` and the reason, without creating placeholder artifacts. Only required images participate in the reference QC gate. Existing `h3_prompt.md` files from older runs may remain canonical through an explicit manifest path; never create a duplicate merely to rename them.
