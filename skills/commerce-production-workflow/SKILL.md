---
name: commerce-production-workflow
description: "Adapt Yingce's short-drama production workflow for ecommerce: create structured product shot rows, black-and-white multi-panel storyboard boards, and spatial/white-mesh previs boards before handing off to prompt and video skills."
---

# Commerce Production Workflow

This skill is based on the Yingce server's `影策短剧制作工作流`. The original workflow, state machine, and Canvas execution references are preserved under [server-workflow](references/server-workflow/).

It is the production-stage companion to `commerce-shot-grammar`:

- `commerce-shot-grammar` handles shot design, axis, camera, storyboard logic, and action-previs continuity;
- this skill handles the ecommerce production order and artifact gates;
- prompt-writing and media submission remain delegated to the user's selected prompt/production skills.

When any approved video-prompt skill supplies a finalized video prompt, use it as the sole creative source for the two image artifacts. Generate the black-and-white storyboard board first, then generate the spatial/white-mesh previs using the accepted storyboard board as a reference. Do not rewrite the source video direction or create a competing prompt.

## Ecommerce production order

Use this order:

```text
product evidence and continuity lock
→ structured product shot rows
→ black-and-white multi-panel storyboard board(s)
→ spatial / white-mesh previs board(s)
→ prompt handoff
→ video generation handoff
```

The storyboard board and spatial/white-mesh previs must be derived from the same shot rows. The previs must preserve the storyboard board's product SKU, creator/hands, surface, background, camera side, lighting direction, product orientation, and mechanism state. It cannot be an independent second illustration.

## Product-specific locks

Before creating artifacts, record:

- SKU/variant, silhouette, proportions, material, finish, color, labels and controls;
- supported product state before and after each operation;
- creator identity, wardrobe, hands and target market/locale;
- environment anchors, surface, lighting and camera side;
- hand ownership, contact point, grip, placement, release and object trajectory;
- the single selling point or mechanism demonstrated in the shot rows.

Unknown product facts remain unknown. Do not invent accessories, dimensions, claims, controls, mechanism states, or visual changes.

## Two artifact stages

1. Create the structured shot rows first. Each row needs timing, shot size, camera position, movement, subject placement, product state, visible action, proof purpose, and continuity start/end state.
2. Generate the black-and-white multi-panel storyboard board from those rows. It is the chronological visual reference and does not replace the rows.
3. Generate the spatial / white-mesh previs board from the same rows and the accepted storyboard board. Show floor or spatial anchors, product/creator placement, hand paths, camera positions, axis and frame safety.
4. Run cross-artifact QC. If the product, hand, creator, scene, camera side, state transition, or target ratio drifts, revise the dependent artifact from the accepted artifact.
5. Hand off both artifacts to the prompt skill. Do not write prompts here and do not claim media generation.

## Required output

Return `sourceVideoPrompt`, `commerceContinuityLock`, `shotRows`, `blackWhiteStoryboardArtifacts`, `whiteMeshPrevisArtifacts`, `crossArtifactQC`, and `promptHandoff`. Every artifact records its source prompt version, shot-row revision, references, target ratio, and status.

Stop before prompt handoff when required product evidence is missing, the storyboard image is unavailable, the action board is inconsistent with the storyboard, or a claim cannot be shown by an observable product action.

If the user explicitly authorizes image generation and the image-generation tool is available, the handoff may continue directly into two sequential image tasks. Persist both task/result statuses; do not report an image as complete from a queued state.
