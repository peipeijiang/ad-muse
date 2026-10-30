---
name: commerce-shot-grammar
description: "Adapt Yingce's 分镜语法 method for ecommerce scenes: establish spatial previs, then derive a linked storyboard while preserving product, hand, prop, scene, axis, and camera continuity."
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

## Planning order

The structured shot rows come first. Then:

1. Establish the `shot-previs` spatial plan: scene geometry, actor and product placement, axis, camera side, camera stations, movement paths, contact relationships, target ratio and safe frames.
2. Derive the `shot-storyboard` from the accepted previs: chronological framing, shot size, viewpoint, camera movement, action start/end state and proof purpose. The storyboard inherits the previs rather than choosing a new geography.

This previs-before-storyboard relationship comes from `shot-previs`, which states that storyboard places the shot sequence on the spatial blueprint. Do not reverse the dependency in a prompt. The production workflow may use a different artifact name such as “white-mesh previs”, but the spatial plan still precedes the chronological board when both are required.

## Card routing

Use the bundled source cards internally:

- `shot-storyboard` for the chronological shot sequence;
- `shot-previs` for the space, blocking and camera blueprint;
- `shot-axis-triangle` and `shot-dialog-blocking` for hand/creator relationships and screen direction;
- `shot-shot-sizes`, `shot-viewpoint` and `shot-open-close` for framing;
- `shot-movement`, `shot-shotflow` and `shot-transitions` for movement and continuity;
- `shot-depth-focus` and the `gfl-*` cards when optical, movement or screen-direction logic matters.

The user does not need to name cards. Choose them from the scene problem and preserve their dependencies.

## Previs image gate

When the route requires a previs image, check:

- one unambiguous scene layout, or clearly separated stage panels;
- no several full copies of one moving actor occupying the same continuous set;
- one solid acting figure per actor plus numbered ghosts only when needed for motion;
- readable camera stations, frusta, axis, paths, action/contact marks and safe frames;
- no miniature storyboard frames pasted in as the spatial map;
- the same product, creator, environment, lighting, camera side and state as the shot rows.

The storyboard then uses the accepted previs and verified product references. A previous storyboard cannot become the spatial source after the fact.

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

If image generation is authorized, submit the previs image first, wait for and inspect the result, then submit the storyboard with the accepted previs and product identity references. Report the real status of each task.
