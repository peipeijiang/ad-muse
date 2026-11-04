---
name: commerce-production-workflow
description: "Adapt Yingce's short-drama production workflow for ecommerce: enforce source, asset and stage gates, create a black-and-white storyboard followed by a linked spatial previs, then hand off to prompt and video skills."
---

# Commerce Production Workflow

This skill adapts the Yingce server's `影策短剧制作工作流` (production workflow: source intake, asset locks, stage gates, media verification and delivery). The original workflow, state machine and Canvas execution references are preserved under [server-workflow](references/server-workflow/). The separate `分镜语法` methodology pack is adapted by `commerce-shot-grammar`.

The two source roles are distinct:

| Source | What it owns | Local adaptation |
| --- | --- | --- |
| `影策短剧制作工作流` | Production order, source/asset gates, structured storyboard creation, delivery states | `commerce-production-workflow` |
| `分镜语法` | Shot grammar, axis, blocking, camera movement, spatial previs and storyboard method cards | `commerce-shot-grammar` |

This skill owns the production order and artifact gates. Prompt-writing and media submission remain delegated to the selected prompt and production skills.

## Local workflow v2.0 — storyboard first

When an approved video-prompt skill supplies the direction, retain its Hook, setting, action and shot order. Adapt product facts only from verified references. The opening Hook must follow the approved storyboard and creative brief, whatever its form: action, problem, result, demonstration, reaction or another established opening. Do not impose a location, pickup action, crowd or camera move from a previous campaign. The spatial map explains the scenes actually present in the storyboard; text/audio-only Hooks stay in the shot data and are not converted into invented physical action.

```text
product evidence and continuity lock
→ shared structured shot rows (Master Shot Data)
→ black-and-white chronological storyboard
→ inspect storyboard
→ white-model spatial previs referencing that storyboard AND product identity images
→ cross-artifact QC and revisions
→ prompt handoff → authorized video generation
```

Plan spatial relationships in the shot rows before either image, but generate the storyboard image first. The storyboard defines visible composition and beat order; the white-model map explains the corresponding space, camera stations and movement. Both use the same shot IDs and revision. If the spatial review exposes an impossible shot, update the rows and affected storyboard panels, then update the previs; do not silently invent a new action.

This image order and the two-board route are local ecommerce adaptations requested by the user, not verbatim Yingce source rules. Historical source cards remain unchanged. For this route, this local order takes precedence over their previs-first image dependency.

Read [layout-and-qc.md](references/layout-and-qc.md) when preparing either board. Generate both planning images through the LK888/upDrama media task with model `tt-image-2.5`; do not substitute another image provider. Record the model, task ID, params, prompt hash and output hash for each image. Prefer the lightweight two-image route; do not introduce a 3D production pipeline unless actual geometric validation is needed or requested.

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

1. Complete shared shot rows: stable shot ID, scene ID, timing, Hook/proof purpose, shot size, viewpoint and height, camera station/side, view direction, movement, subject/product start and end positions, environment anchors, product orientation, hand/contact/release, transition and target frame ratio. Mark unknown facts; do not fabricate precision.
2. Generate a black-and-white storyboard from the approved direction, rows and verified product references. Default to six chronological panels in three columns by two rows; adapt the count when the user explicitly requests another layout or the story cannot be represented without losing essential beats. Each panel carries its shot ID and shows the actual composition, action and Hook environment. For vertical video, each image panel must have a real 9:16 image area, regardless of sheet ratio. Inspect product, sequence and hand states before proceeding. Generate it through the LK888/upDrama media task with `tt-image-2.5`; record the model, task ID, params and output hash.
3. Generate a grayscale white/clay-model spatial board using the inspected storyboard, the SAME rows and product identity images as references. Use the dominant spatial map, right product/legend strip and compact bottom camera-card strip described in the layout guide. Do not independently regenerate the narrative. Generate it through the LK888/upDrama media task with `tt-image-2.5`; record the model, task ID, params, prompt hash and output hash.
4. Compare every shot ID across rows and both boards. Check Hook setting/action, product identity/scale, hand state, placement/release, scene anchors, camera side, movement and target framing. Fix incorrect or unreadable labels using deterministic overlay when feasible, rather than regenerating the whole image. Revise affected artifacts when staging is wrong.
5. Record exact revisions, reference dependencies and QC evidence. Distinguish conceptual visual checks, measured geometry checks (if any), and user acceptance. A generated image with camera arrows is not proof of measured field of view, collision clearance or dimensions. Never promote unchecked items to pass.
6. Hand off both images and verified product references to the selected prompt skill after required checks. Preserve pending user-review gates when the user requested final approval. Prompt writing and video submission remain owned by their respective skills.

## Required output

Return `sourceVideoPrompt`, `commerceContinuityLock`, `shotRows`, `blackWhiteStoryboardArtifacts`, `whiteMeshPrevisArtifacts`, `crossArtifactQC`, and `promptHandoff`. Each artifact records source prompt version, shot-row revision, input reference paths/task IDs, sheet ratio, shot frame ratio, source snapshot/version when known and actual status.

Stop handoff on missing required product evidence, unavailable images, contradictory actions or identity, or unsupported claims. For unmeasured geometric properties, explicitly report `not_verified`; require measured validation only when the task calls for it. Do not confuse a conceptual-board pass with a measured or user-approved pass.

When image generation is authorized, generate and inspect the storyboard first, then submit the previs with the storyboard and product references. Persist task IDs before polling, reuse known tasks on uncertain responses, and distinguish queued, completed, downloaded and reviewed. Paid video generation requires its own authorized scope.
