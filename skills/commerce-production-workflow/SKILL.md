---
name: commerce-production-workflow
description: "Adapt Yingce's short-drama production workflow for ecommerce: enforce source, asset and stage gates, create a spatial previs and a linked black-and-white storyboard, then hand off to prompt and video skills."
---

# Commerce Production Workflow

This skill adapts the Yingce server's `影策短剧制作工作流` (production workflow: source intake, asset locks, stage gates, media verification and delivery). The original workflow, state machine and Canvas execution references are preserved under [server-workflow](references/server-workflow/). The separate `分镜语法` methodology pack is adapted by `commerce-shot-grammar`.

The two source roles are distinct:

| Source | What it owns | Local adaptation |
| --- | --- | --- |
| `影策短剧制作工作流` | Production order, source/asset gates, structured storyboard creation, delivery states | `commerce-production-workflow` |
| `分镜语法` | Shot grammar, axis, blocking, camera movement, spatial previs and storyboard method cards | `commerce-shot-grammar` |

This skill owns the production order and artifact gates. Prompt-writing and media submission remain delegated to the selected prompt and production skills.

When an approved video-prompt skill supplies the canonical direction, use it as the creative source for the planning artifacts. Generate the spatial previs after the structured shot rows, then derive the black-and-white storyboard from the accepted spatial plan. Do not rewrite the source video direction or create a competing prompt.

## Ecommerce production order

Use this order:

```text
product evidence and continuity lock
→ structured product shot rows
→ spatial / white-mesh previs board(s)
→ black-and-white multi-panel storyboard board(s)
→ prompt handoff
→ video generation handoff
```

Both boards derive from the same complete shot rows. The previs is the spatial source of truth for scene geometry, camera side, axis and contact; the storyboard inherits that accepted layout while adding chronological compositions. Neither artifact may become an independent illustration.

**Previs is a spatial planning artifact, not a second storyboard render.** The `shot-previs` card in `分镜语法` establishes the spatial blueprint before `shot-storyboard` places the shot sequence on that geometry. The storyboard answers “what is seen, and in what order”; the previs answers “where the subject, product and cameras are in the scene, and how do they move?”

The source `影策短剧制作工作流` requires a structured production storyboard and a black-and-white multi-panel board; its white-model preview is an optional tool used when the user requests spatial blocking or motion preview. Making a white/mesh previs a mandatory ecommerce planning artifact, and placing it before the board, is an adaptation in this skill. Record that adaptation explicitly instead of presenting it as verbatim source behaviour.

## Product-specific locks

Before creating artifacts, record:

- SKU/variant, silhouette, proportions, material, finish, color, labels and controls;
- supported product state before and after each operation;
- creator identity, wardrobe, hands and target market/locale;
- environment anchors, surface, lighting and camera side;
- hand ownership, contact point, grip, placement, release and object trajectory;
- the single selling point or mechanism demonstrated in the shot rows.

Unknown product facts remain unknown. Do not invent accessories, dimensions, claims, controls, mechanism states, or visual changes.

## Planning artifact stages

1. Complete the structured shot rows before requesting either image. Every row must include timing; shot size; viewpoint and camera height/angle; camera position relative to the subject and axis; camera movement path and direction; subject and product positions in the scene and frame; stable spatial/environment anchors; product orientation/state; visible action and hand path/contact; proof purpose; continuity start/end state; and the intended safe-frame bounds. Do not proceed while a required camera or blocking field is missing or vague.
2. Build the spatial / white-mesh previs from those rows. Use a coherent single scene layout, or clearly separated stage panels. Do not place several full copies of a moving actor in one continuous scene. Draw one canonical position per actor per stage and a labelled motion path; if ghost positions are useful, identify them as numbered stages and keep one solid acting figure. Include the product, surface/environment anchors, camera stations, viewing directions/frusta, contact path, scene axis/180-degree line, and each camera's safe frame. Use readable symbols and a legend. Do not paste miniature storyboard frames into the spatial map.
3. Generate the black-and-white multi-panel storyboard from the accepted previs. It is the chronological visual reference and does not replace the rows or previs. Its panels communicate the selected shot compositions and beat order while inheriting the accepted scene side, axis, product state and spatial relationships.
4. Before handoff, compare every row against both artifacts: positions, camera stations/frusta, paths, axis and safe frames against the previs; framing and beat order against the storyboard. Missing fields, contradictory duplicate staging, unreadable marks, miniature board frames used as the spatial map, or an incomplete image are failures. Revise the dependent artifact; do not waive the gate with a `pass` label.
5. Run cross-artifact QC. If product, hand, creator, scene, camera side, state transition or target ratio drifts, revise the dependent artifact from the accepted upstream artifact. Record the check against each row and each exact image revision.
6. Hand off both artifacts to the prompt skill. Do not write prompts here and do not claim media generation.

## Required output

Return `sourceVideoPrompt`, `commerceContinuityLock`, `shotRows`, `whiteMeshPrevisArtifacts`, `blackWhiteStoryboardArtifacts`, `crossArtifactQC`, and `promptHandoff`. Every artifact records its source prompt version, shot-row revision, references, target ratio, source snapshot or deployment version when known, and status.

Stop before prompt handoff when required product evidence is missing, the previs or storyboard is unavailable, the action board disagrees with the accepted spatial plan, or a claim cannot be shown by an observable product action.

If the user explicitly authorizes image generation and the image-generation tool is available, continue into the sequential previs and storyboard tasks. Persist both task/result statuses; do not report an image as complete from a queued state.
