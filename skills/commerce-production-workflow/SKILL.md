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

The storyboard board and spatial/white-mesh previs must be derived from the same complete shot rows. The previs must preserve the storyboard board's product SKU, creator/hands, surface, background, camera side, lighting direction, product orientation, and mechanism state. It cannot be an independent second illustration.

**Previs is a spatial planning artifact, not a second storyboard render.** Plan its camera and blocking information before creating either image. Never prompt the image model to reproduce the storyboard's panel compositions, match every storyboard camera view, or merely convert those panels into wireframe/white-mesh style. The storyboard answers “what is seen, and in what order”; the previs answers “where are the subject, product and cameras in the scene, and how do they move?” Keep the two artifacts linked through the same shot rows while making their visual functions distinct.

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

1. Create and complete the structured shot rows before requesting either image. Every row must include: timing; shot size; viewpoint and camera height/angle; camera position relative to the subject and axis; camera movement path and direction; subject and product positions in the scene and frame; stable spatial/environment anchors; product orientation/state; visible action and hand path/contact; proof purpose; continuity start/end state; and the intended safe-frame bounds. Do not proceed to image generation while any required camera or blocking field is missing or vague. Use explicit values or scene-relative descriptions that can be drawn; “cinematic,” “close-up,” or “camera moves smoothly” alone are not executable spatial instructions.
2. Generate the black-and-white multi-panel storyboard board from those rows. It is the chronological visual reference and does not replace the rows. Its panels communicate the selected shot compositions and beat order.
3. Generate the spatial / white-mesh previs board from those rows, using the accepted storyboard only to lock identity, scene, product state and continuity. Make it a legible overhead or oblique scene-layout/previsualization view (or a clearly separated layout plus camera/framing views when one view cannot carry the information). Explicitly draw and label the subject, product, surface/environment anchors, each camera station and viewing direction/frustum, the action/contact path, the camera movement path, the scene axis/180-degree line, and each camera's safe frame. Use distinct, readable symbols and a legend where needed. Camera stations, frusta, axis, paths and safe-frame bounds must be prominent planning information in the image, never tiny edge decorations. Keep the same scene side, lighting direction, product orientation and mechanism state as the shot rows/storyboard; do not copy the storyboard panels as the previs layout.
4. Before handing off, compare every shot row against the previs plan: confirm all required spatial fields are represented, the drawn camera stations/frusta and paths match the row data, axis and safe-frame bounds are unambiguous, and the previs communicates scene geometry rather than repeating storyboard compositions. Missing fields, unreadable/missing spatial marks, a storyboard-as-wireframe result, or an incomplete image are generation failures: revise the planning inputs and regenerate before proceeding. Do not waive these requirements by marking QC `pass`.
5. Run cross-artifact QC. If the product, hand, creator, scene, camera side, state transition, or target ratio drifts, revise the dependent artifact from the accepted artifact. Record the check against each row and the exact previs image revision.
6. Hand off both artifacts to the prompt skill. Do not write prompts here and do not claim media generation.

## Required output

Return `sourceVideoPrompt`, `commerceContinuityLock`, `shotRows`, `blackWhiteStoryboardArtifacts`, `whiteMeshPrevisArtifacts`, `crossArtifactQC`, and `promptHandoff`. Every artifact records its source prompt version, shot-row revision, references, target ratio, and status.

Stop before prompt handoff when required product evidence is missing, the storyboard image is unavailable, the action board is inconsistent with the storyboard, or a claim cannot be shown by an observable product action.

If the user explicitly authorizes image generation and the image-generation tool is available, the handoff may continue directly into two sequential image tasks. Persist both task/result statuses; do not report an image as complete from a queued state.
