---
name: commerce-shot-grammar
description: "Adapt Yingce's server-side shot grammar for ecommerce scenes: plan a product storyboard and a linked action previs while preserving product, hand, prop, scene, axis, and camera continuity."
---

# Commerce Shot Grammar

This skill is based on the Yingce server's `分镜语法` package. Its source is preserved in [server-shot-grammar.md](references/server-shot-grammar.md), with the complete `shot-*` and `gfl-*` card suite under [server-shot-suite](references/server-shot-suite/).

It handles shot design and visual planning only. Prompt writing, image-model parameters, product claims, and paid generation belong to the other skills in the project and must not be invented here.

When an approved video prompt is supplied by any prompt-writing skill or by the user, treat that prompt as the canonical creative source. Derive the storyboard and action-previs image tasks from its visible timeline, product, subject, scene, camera, and state constraints. Do not invent a competing creative direction or rewrite the source video prompt itself.

## Ecommerce adaptation

Keep the server shot grammar as the camera and staging foundation, then add one continuity layer for the product scene:

- product SKU, variant, silhouette, proportions, material, color, label/control placement;
- product state before and after each action;
- hand ownership, contact point, grip, placement and release;
- creator/subject identity, wardrobe, screen position and eyeline;
- environment anchors, surface, light direction and camera side;
- supported proof moment and the exact visible mechanism.

Do not design a shot that changes product geometry, invents an accessory, relocates the environment, or changes the hand holding the product without a visible transfer.

## Default two-artifact output

Produce two linked planning artifacts in order:

1. **`shot-previs`:** the spatial/action previsualization from the server grammar, establishing scene geometry, subject/product placement, axis, camera side, frame ratio, movement path and contact relationships.
2. **`shot-storyboard`:** the chronological storyboard derived from the accepted `shot-previs`, with shot size, viewpoint, camera position, movement, subject/product state and action purpose.

The `shot-storyboard` must reference the accepted `shot-previs` and inherit its product, subject, environment, lighting, axis, camera side, and timeline. Never generate the two artifacts independently.

## Card routing

Use the bundled server cards internally:

- `shot-storyboard` for the chronological storyboard;
- `shot-previs` for the action/spatial previsualization;
- `shot-axis-triangle` and `shot-dialog-blocking` for hand/creator relationships and screen direction;
- `shot-shot-sizes`, `shot-viewpoint`, and `shot-open-close` for framing;
- `shot-movement`, `shot-shotflow`, and `shot-transitions` for camera and continuity;
- `shot-depth-focus` and the `gfl-*` cards when optical or movement grammar matters.

The user does not need to name cards. Select them from the scene problem and preserve their dependencies.

## Required output fields

Return:

- `productContinuityLock`;
- `shotTable`;
- `screenDirectionAndBlocking`;
- `shotPrevisArtifact`;
- `shotStoryboardArtifact`;
- `crossArtifactContinuityCheck`;
- `sourceVideoPrompt` and its version/source reference;
- `promptHandoff` stating which approved video-prompt skill supplied the source. This skill does not draft or replace that prompt.

The final handoff must explicitly say that prompt construction and media submission are delegated to the relevant prompt/production skill. This skill never claims that images or video were generated.

If image generation is explicitly authorized and a generation tool is available, submit Image 1 first, wait for its result, then submit Image 2 with Image 1 as a reference. Report the real result status for each image.

## Quality gate

Fail the handoff if the two artifacts disagree about product identity, creator/hand, environment, lighting, axis, camera side, action order, mechanism state, target ratio, or proof visibility. Regenerate or revise the dependent artifact from the accepted anchor; do not reconcile inconsistencies by inventing a third product state.
