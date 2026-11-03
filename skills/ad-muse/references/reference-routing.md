# Reference routing — complementary product images and appropriate planning

## Scope and artifact families

Apply to any product category or setting. Read the current brief, product dossier, shot rows and final prompt. Evaluate identity, interaction, state/time, space and reference coverage. Do not prescribe a location, presenter, market or Hook.

Use only the existing artifact families:

1. Product reference set: same-SKU source photos, different views, details, scale and product-in-use context; optionally a source-verified identity sheet.
2. Black-and-white storyboard: composition, actions, state transitions and chronological continuity.
3. White-model previs: layout, relative positions, contact, occlusion, axis and camera geometry, referencing the inspected storyboard.

A product-in-use photo is a product reference, not a new generated artifact type. Do not generate a separate “operation image,” operation sheet or operation route.

## Product-image selection

Review the available product inventory before selecting. Prefer complementary images that together explain silhouette, relevant front/back/side views, controls/material details, proportion and real usage/fit where applicable. Include an accurate usage-context photo when it resolves how the product relates to a body, surface, environment or other object. This is not restricted to wearables or hand-held goods.

Do not automatically choose only the hero image, nor require a fixed minimum image count. Record what each image contributes. Multiple images are preferred when they close distinct gaps; a single image is acceptable when sufficient. Verify exact SKU, orientation and state; exclude conflicting variants and reject anatomical distortions or inaccurate products in usage images. Original photos are not automatically correct. Generated identity sheets must be checked against source evidence.

Record `product_reference_review` with nonempty observations for `appearance`, `angles_details`, `usage_context`, and `selection_reason`. Say when a category is not applicable and why; when evidence is missing, record the gap rather than calling it covered. Do not create missing product facts via generation.

## Choose the planning depth

- Simple static views or stable use can use product references alone if appearance and relevant usage are adequately covered.
- Identity ambiguity may need an identity sheet, within the product-reference family.
- Contact actions, two-hand coordination, grip changes, state changes, causal sequences and important continuity require a storyboard. Describe before/during/after states there; do not add another image stage.
- Important occlusion, installation, transfer, actor interaction, directional effects or complex spatial/camera geometry require storyboard plus previs. Separate unrelated scenes do not alone trigger previs. Assess the spatial dependency itself.
- Stable wearing or stable surface contact requires usage-context coverage in the product set, not automatically a storyboard/previs. This photo must show the relevant fit/relationship, not merely carry a “use context” label.
- A prior anatomy failure triggers storyboard reassessment and contact/ownership checks; add previs if the underlying spatial factors require it. Do not just repeat a failed prompt with “no extra fingers.”

For risky hand interactions, record actor/hand ownership, start/end state, target, occlusion and release in shot rows and storyboard; explain spatial contact in previs when needed. Do not demand five visible fingers when natural occlusion hides some. Preserve the actual product function and creative direction.

## Machine-readable contract

`routing_version: 2`, backend and the existing four modes remain. `operation_plus_product` and the `operation` image purpose are removed and must be reassessed, not silently renamed.

Record `shot_rows_sha256`, `prompt_sha256`, `product_reference_review`, and one `shot_assessments` entry per unique `shot_id`. Each entry needs `evidence` and explicit boolean `risks`:

`wearing_fit`, `finger_contact`, `two_hand_interaction`, `grip_change`, `occlusion`, `installation`, `transfer`, `multi_actor_interaction`, `directional_effect`, `complex_camera`, `identity_ambiguity`, `prior_anatomy_failure`, `temporal_continuity`, `mechanism_state`, `material_change`, `surface_contact`, `contents_transfer`, `interface_action`.

Risk flags describe actual shot requirements, not keywords in the product title. Unknown is not false. If a new material risk is not represented, record it and extend assessment instead of forcing a low-risk classification.

Each selected reference has an absolute `path`, matching `sha256`, `qc: pass`, readable `role`, `visual_qc` observations, `covers_shots`, and `purposes` chosen from `identity`, `identity_sheet`, `usage_context`, `storyboard`, `previs`. `usage_context` is a coverage tag on a product reference, not a separate artifact or mode. One image may serve more than one purpose only if visually verified. Product images collectively cover required identity and use; planning images cover action/space.

The validator checks declared coverage and stale inputs; request preparation additionally checks backend limits. Neither can inspect actual anatomy. Use original product evidence to correct wrong reference imagery, update affected rows/boards and rerun QC. No image count or board can guarantee a correct render.

## QC

Inspect selected product views against SKU and source evidence. Check storyboard actions and hand/object ownership; check previs spatial relations. For final video, inspect contact, occlusion, release and cuts using contiguous frames around suspicious events. Record timestamps and failures; technical decoding is not creative acceptance. Preserve human review gates when requested.
