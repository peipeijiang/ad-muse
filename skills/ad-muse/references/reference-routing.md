# Reference routing — complementary product images and appropriate planning

## Scope and artifact families

Apply to any product category or setting. Read the current brief, product dossier, shot rows and final prompt. Evaluate identity, interaction, state/time, space and reference coverage. Do not prescribe a location, presenter, market or Hook.

Use only the existing artifact families:

1. Product reference set: same-SKU source photos, different views, details, scale and product-in-use context; optionally a source-verified identity sheet.
2. Color storyboard: composition, actions, state transitions and chronological continuity.
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

New variants use `routing_version: 3`. Existing v2 plans retain their coverage and validation behavior. `operation_plus_product` and the `operation` image purpose are removed and must be reassessed, not silently renamed.

Record `shot_rows_sha256`, `prompt_sha256`, `product_reference_review`, and one `shot_assessments` entry per unique `shot_id`. Each entry needs `evidence` and explicit boolean `risks`:

`wearing_fit`, `finger_contact`, `two_hand_interaction`, `grip_change`, `occlusion`, `installation`, `transfer`, `multi_actor_interaction`, `directional_effect`, `complex_camera`, `identity_ambiguity`, `prior_anatomy_failure`, `temporal_continuity`, `mechanism_state`, `material_change`, `surface_contact`, `contents_transfer`, `interface_action`.

Risk flags describe actual shot requirements, not keywords in the product title. Unknown is not false. If a new material risk is not represented, record it and extend assessment instead of forcing a low-risk classification.

Each selected reference has an absolute `path`, matching `sha256`, `qc: pass`, readable `role`, `visual_qc` observations, `covers_shots`, and `purposes` chosen from `identity`, `identity_sheet`, `usage_context`, `storyboard`, `previs`. `usage_context` is a coverage tag on a product reference, not a separate artifact or mode. One image may serve more than one purpose only if visually verified. Product images collectively cover required identity and use; planning images cover action/space.

The validator checks declared coverage and stale inputs; request preparation additionally checks backend limits. Neither can inspect actual anatomy. Use original product evidence to correct wrong reference imagery, update affected rows/boards and rerun QC. No image count or board can guarantee a correct render.

### V3 planning and submission

- Set `reference_video` and `speech_fidelity` to explicit booleans. `reference_video` means the variant is adapting a specified source, and `speech_fidelity` means its source speech needs local ASR. Preserve the source analysis and cut mapping in the existing run evidence. Source evidence stays local unless separately selected and authorized for transfer.
- When a spatial risk is flagged, set `spatial_dependency` in that shot assessment and explain the decision in its existing `evidence` field. Use `true` when occlusion, clearance, placement or camera geometry must be resolved to show the action. A clear, fixed-view installation may use a board alone.
- Before drawing, run `python3 scripts/validate_reference_plan.py <variant-dir> --plan-only` from the skill directory. The result derives `production_tier`, `reference_mode`, `required_coverage`, `required_artifacts` and `required_checks`. The optional existing `mode` field can raise the reference minimum for an explicit requirement. `minimum_production_tier` optionally raises review depth for user-requested review without adding images. The returned fields describe one decision; avoid copying them into another manifest. Required identity and usage purposes carry forward under any mode. A selected storyboard sets a standard floor; replication, unresolved spatial dependencies requiring previs, or a prior anatomy failure raise review depth to high.
- For a required board, store `storyboard` in the same plan, with `status: required`, local `path`, `sha256`, delivered `width`/`height`, `image_provider`, `image_fallback`, and `grid` (`columns`, `rows`, `reading_order: row-major`, `cell_aspect_ratio`, `board_layout_ratio`, `provider_transport_ratio`). Use row-major `planned_cells` (`cell_id`, `shot_ids`, `proof_id`) and `observed_cells` (`cell_id`, `shot_ids_observed` as an array, `proof_id`, `bounds` as pixel `[x,y,width,height]`, `status`, `visible_proof`). After visual approval, use `review_digest(board, shot_rows_sha256)` from `scripts/validate_storyboard_contract.py` to record `storyboard.review_sha256`. Refresh it only after reviewing changes to board bytes, mapping or shot rows. Attach the reviewed board once under the `storyboard` purpose, with shot coverage matching the observed cells. Internal optional previews stay outside `selected_images` on no-board routes. The offline validator checks the records and local bytes. It does not recognize products or verify remote URL contents.
- For submission, run the normal validator without `--plan-only`. It checks current shot and final-prompt hashes, applicable board records and all selected reference purposes. Old v3 drafts made under the partial board-only contract need their missing assessment and mapping fields filled in before preparing a new request. Continue known remote tasks by their recorded IDs.

## QC

Inspect selected product views against SKU and source evidence. Check storyboard actions and hand/object ownership; check previs spatial relations. For final video, inspect contact, occlusion, release and cuts using contiguous frames around suspicious events. Record timestamps and failures; technical decoding is not creative acceptance. Preserve human review gates when requested.
