---
name: commerce-production-workflow
description: "Adapt Yingce's short-drama production workflow for ecommerce: enforce source, asset and stage gates, create an evidence-led color storyboard followed by a linked spatial previs when needed, then hand off to prompt and video skills."
---

# Commerce Production Workflow

This skill adapts the Yingce server's `影策短剧制作工作流` (production workflow: source intake, asset locks, stage gates, media verification and delivery). The original workflow, state machine and Canvas execution references are preserved under [server-workflow](references/server-workflow/). The separate `分镜语法` methodology pack is adapted by `commerce-shot-grammar`.

The two source roles are distinct:

| Source | What it owns | Local adaptation |
| --- | --- | --- |
| `影策短剧制作工作流` | Production order, source/asset gates, structured storyboard creation, delivery states | `commerce-production-workflow` |
| `分镜语法` | Shot grammar, axis, blocking, camera movement, spatial previs and storyboard method cards | `commerce-shot-grammar` |

This skill owns the production order and artifact gates. Prompt-writing and media submission remain delegated to the selected prompt and production skills.

## Local workflow v2.1 — draft before storyboard, storyboard before previs

When an approved video-prompt skill supplies the direction, retain its Hook, setting, action and shot order. Adapt product facts only from verified references. The opening Hook must follow the approved storyboard and creative brief, whatever its form: action, problem, result, demonstration, reaction or another established opening. Do not impose a location, pickup action, crowd or camera move from a previous campaign. The spatial map explains the scenes actually present in the storyboard; text/audio-only Hooks stay in the shot data and are not converted into invented physical action.

```text
product evidence and continuity lock
→ shared structured shot rows (Master Shot Data)
→ non-submittable action prompt draft
→ color chronological storyboard prompt and image
→ inspect storyboard
→ white-model spatial previs when spatial risk requires it
→ cross-artifact QC and revisions
→ prompt handoff → authorized video generation
```

Plan spatial relationships in the shot rows before either image, but generate the storyboard image first. The storyboard defines visible composition and beat order; the white-model map explains the corresponding space, camera stations and movement. Both use the same shot IDs and revision. If the spatial review exposes an impossible shot, update the rows and affected storyboard panels, then update the previs; do not silently invent a new action.

This image order and the two-board route are local ecommerce adaptations requested by the user, not verbatim Yingce source rules. Historical source cards remain unchanged. For this route, this local order takes precedence over their previs-first image dependency.

Read [layout-and-qc.md](references/layout-and-qc.md) when preparing either board. This skill owns the AdMuse storyboard writer and produces one `storyboard_prompt.md` from `shot_rows.json`, `action_prompt_draft.md`, Hypit evidence when present, and verified same-SKU references. PostPlus supplies the content structure, ZenStory supplies still-frame description, EvoLink supplies the borderless sheet direction, and LearnPrompt supplies reference-role wording. These sources inform the prompt and do not create extra runtime stages.

Generate one color sheet with natural phone-camera exposure, white balance, material texture and source-faithful product markings. Do not add borders, gutters, labels, timestamps or decorative text. Use six meaningful cells by default for a vertical target, prefer two columns by three rows, use three columns by two rows when channel geometry or readability requires it, and use three by three only for additional required evidence that remains readable. Record board, cell, provider and video ratios separately. The image router receives explicit `tt-image-2.6` and no automatic fallback. Store planned and observed cell-to-shot mappings outside the image. Inspect the exact delivered board before downstream use. A failed required board blocks the route. A failed optional board may be omitted only when a valid no-board route was selected beforehand.

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

1. Complete shared shot rows with stable shot ID, scene ID, timing, Hook/proof purpose, shot size, viewpoint, camera side, movement, subject/product start and end positions, environment anchors, product orientation, hand/contact/release, transition and target frame ratio. Mark unknown facts.
2. Write `storyboard_prompt.md` after the action draft and before image generation. Use a short shared continuity block and detailed visible cell descriptions. Each cell states framing, viewpoint, subject and hand placement, product state and proof. Keep timing, dialogue and continuous motion in the shot rows and action draft. Store planned cell-to-shot mapping in the manifest.
3. Generate and inspect one color storyboard sheet from the prompt and verified product references. Use six meaningful cells by default, two columns by three rows for a vertical target, three columns by two rows when needed, and three by three only when six cells cannot cover required evidence while retaining readability. Record model, task ID, params, prompt hash and input/output hashes.
4. Generate a grayscale white/clay-model spatial board using the inspected storyboard, same rows and product identity images only when spatial risk requires it. Do not independently regenerate the narrative. Record its model, task ID, params, prompt hash and input/output hashes.
5. Compare selected cells and shot IDs across rows, storyboard and any previs. Check Hook setting/action, product identity/scale, hand state, placement/release, scene anchors, camera side, movement and target framing. Record observed cell bounds and visible proof. Missing, merged, reordered or unreadable required proof fails the storyboard gate.
6. Record revisions, dependencies and QC. Distinguish visual concept, measured geometry and user acceptance. Any upstream edit invalidates affected downstream QC.
7. Hand off the accepted storyboard, observed cell manifest and verified product references to the selected prompt skill. Preserve pending user-review gates when requested. Prompt writing and video submission remain owned by their respective skills.

## Required output

Return `sourceVideoPrompt`, `commerceContinuityLock`, `shotRows`, `actionPromptDraft`, `storyboardPrompt`, `colorStoryboardArtifacts`, `storyboardCellManifest`, `whiteMeshPrevisArtifacts`, `crossArtifactQC`, and `promptHandoff`. Each artifact records source prompt version, shot-row revision, input reference paths/task IDs, grid and cell ratio, provider transport ratio, source snapshot/version when known and actual status.

Stop handoff on missing required product evidence, unavailable images, contradictory actions or identity, or unsupported claims. For unmeasured geometric properties, explicitly report `not_verified`; require measured validation only when the task calls for it. Do not confuse a conceptual-board pass with a measured or user-approved pass.

When image generation is authorized, generate and inspect the storyboard first, then submit the previs with the storyboard and product references. Persist task IDs before polling, reuse known tasks on uncertain responses, and distinguish queued, completed, downloaded and reviewed. Paid video generation requires its own authorized scope.
