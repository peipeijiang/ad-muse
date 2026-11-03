---
name: commerce-shot-grammar
description: "Adapt Yingce's 分镜语法 method for ecommerce scenes: create a storyboard, then a linked spatial previs while preserving product, hand, prop, scene, axis, and camera continuity."
---

# Commerce Shot Grammar

This skill adapts the Yingce `分镜语法` methodology pack. The source package summary is preserved verbatim at [server-shot-grammar.md](references/server-shot-grammar.md); the copied `shot-*` and `gfl-*` cards are under [server-shot-suite](references/server-shot-suite/). Their hashes match the local Yingce source snapshot.

This is the shot-method layer, not the production gate layer. The companion `commerce-production-workflow` adapts `影策短剧制作工作流` and owns source/asset gates, artifact status and delivery. It does not own the shot cards.

The original `分镜语法` package delivers a shot table, a screen-direction relationship diagram and a 14-field shot card. Its method cards describe spatial previs and storyboard relationships; they do not require generated image files. The local two-image previs/storyboard route is an ecommerce adaptation.

When an approved video-prompt skill supplies the canonical direction, use it as the source for the shot plan and planning images. Do not invent a competing creative direction.

## Ecommerce adaptation

Keep the server shot grammar as the camera, staging and continuity foundation, then add the product layer:

- product SKU, variant, silhouette, proportions, material, color and label/control placement;
- product state before and after each action;
- hand ownership, contact point, grip, placement and release;
- creator/subject identity, wardrobe, screen position and eyeline;
- environment anchors, surface, light direction and camera side;
- supported proof moment and the exact visible mechanism.

Do not design a shot that changes product geometry, invents an accessory, relocates the environment or changes the hand holding the product without a visible transfer.

## Planning order — local v2.0

Structured shot rows come first, including spatial blocking and camera intent. Generate the black-and-white chronological storyboard from those rows and product references; inspect it; then generate the white-model spatial map using that storyboard, the same rows and product references.

The companion `commerce-production-workflow` owns this local image sequence and its [layout/QC guide](../commerce-production-workflow/references/layout-and-qc.md). Historical source cards describe a spatial-blueprint-first method; retain that spatial reasoning in the rows, but do not use it to reverse the user-requested image generation order. This is an explicit local adaptation.

Preserve the approved storyboard's opening Hook, including environment, action, viewpoint and motion where present. Never add a warehouse, store, pickup action or other campaign-specific trope unless the current storyboard calls for it. The map must explain the storyboard's staging. If it reveals a conflict, revise shared rows and dependent images together.

## Card routing

Use the bundled source cards internally:

- `shot-storyboard` for the chronological shot sequence;
- `shot-previs` for the space, blocking and camera blueprint;
- `shot-axis-triangle` and `shot-dialog-blocking` for hand/creator relationships and screen direction;
- `shot-shot-sizes`, `shot-viewpoint` and `shot-open-close` for framing;
- `shot-movement`, `shot-shotflow` and `shot-transitions` for movement and continuity;
- `shot-depth-focus` and the `gfl-*` cards when optical, movement or screen-direction logic matters.

The user does not need to name cards. Choose them from the scene problem; apply the local image sequence above when historical dependencies differ.

## Previs image gate

When the route requires a previs image, check:

- one unambiguous scene layout, or clearly separated stage panels;
- no several full copies of one moving actor occupying the same continuous set;
- one solid acting figure per actor plus numbered ghosts only when needed for motion;
- readable camera stations, frusta, axis, paths, action/contact marks and safe frames;
- spatial map remains dominant; compact bottom shot/camera cards are allowed, with optional targeted framing previews; do not replace the map with a complete redrawn storyboard;
- the same product, creator, environment, lighting, camera side and state as the shot rows.

The previs uses the inspected storyboard and verified product references. Label conceptual frusta and axes as schematic; do not claim measured optics or dimensions from a generated image. Preserve real per-panel aspect ratios in framing previews, not only a ratio label.

## Required output fields

Return:

- `productContinuityLock`;
- `shotTable` or `shotRows`;
- `screenDirectionAndBlocking`;
- `shotPrevisArtifact`;
- `shotStoryboardArtifact`;
- `crossArtifactContinuityCheck`;
- `sourceVideoPrompt` and its version/source reference;
- `promptHandoff` naming the approved prompt skill.

Prompt construction and media submission are delegated to the relevant prompt/production skill. This skill does not claim that images or video were generated.

## Quality gate

Fail the handoff when the two artifacts disagree on product identity, creator/hand, environment, lighting, axis, camera side, action order, mechanism state, target ratio or proof visibility. Revise the dependent artifact from the accepted upstream artifact; do not reconcile a contradiction by inventing a third state.

If image generation is authorized, submit the storyboard image first, wait for and inspect the result, then submit the previs with that storyboard and product identity references. Report the real status of each task.
