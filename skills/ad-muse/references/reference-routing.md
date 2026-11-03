# Reference routing v2 — action and evidence first

## Universal scope

This is a commerce-production router for any product category and creative setting. It does not prescribe warehouses, homes, stores, presenters, body types, hand-held products or a market/language. Read those choices from the current brief and approved creative direction. Route per shot by evidence gaps in five dimensions:

1. Identity: geometry/appearance, variant, contents, interface or other defining attributes.
2. Interaction: actor/object, object/object, body fit, tool/surface, material or interface contact.
3. State and time: start state, action, observable result, transition and continuity.
4. Space: relative positions, scale, occlusion, attachment, movement and camera visibility.
5. Coverage: which verified existing references show each required fact, and what is missing.

Risk flags are features, not a list of permitted scenes. Assess previously unseen actions through these dimensions. If a material risk cannot be represented, record it and extend the assessment before submission rather than declaring every flag false. Do not turn these examples into mandatory shot templates.

## Assessment

Assess each shot after reading the actual shot rows and final prompt. Assign stable shot IDs. Required boolean risk fields (unknown is not false):

`wearing_fit`, `finger_contact`, `two_hand_interaction`, `grip_change`, `occlusion`, `installation`, `transfer`, `multi_actor_interaction`, `directional_effect`, `complex_camera`, `identity_ambiguity`, `prior_anatomy_failure`, `temporal_continuity`, `mechanism_state`, `material_change`, `surface_contact`, `contents_transfer`, `interface_action`.

Include an `evidence` explanation per shot. Stable wearing still needs body-fit evidence even without fastening or removal. A finger tapping a phone next to a worn product is finger contact; two hands with distinct roles require ownership planning. Single-hand steady holding is not automatically high risk. Scene count and temporal continuity are evaluated separately. A written “no extra fingers” instruction is not pose evidence.

## Routing decisions, not one workflow for every product

Use three independent questions: is product identity adequately shown; is the intended action/contact adequately shown; is temporal/spatial continuity adequately constrained? Evaluate the actual shot, not a label such as “wearable” or “simple.”

Examples: static packshots can use source images only; a stable worn product needs fit coverage but may use an existing faithful wearing photo without generating a board; a finger press followed by a visible result needs operation coverage and a storyboard for the causal sequence; fastening behind an occluding wrist or handing a product to another person also needs spatial previs. A sequence of independent beauty shots does not need a board solely because it has cuts. For a simple scene the previs can be one clear map, not a six-scene template.

The router decides the minimum sufficient artifacts and records WHY each is needed or omitted. It never forces both boards for every product and never defaults to originals just because SKU appearance is clear. Planning type and image origin are separate: a verified source operation photo can fill a gap; an unrelated generated image cannot.

## Coverage

- Always require `identity` evidence. Source references remain authoritative for SKU and mechanism.
- Body fit, contact/handling, attachment/transfer, mechanism operation, material change, surface interaction, contents movement, interface action or prior anatomy failure require `operation` evidence covering affected shot IDs. This may be a body pose, object contact, state diagram, material/result reference or interface keyframe as appropriate; it does not require a human hand.
- `temporal_continuity` requires a `storyboard` covering the sequence: causal actions, reveal/proof order, changed hand/object states or important continuity across cuts. Several independent static packshots alone do not trigger it. A single shot containing several consequential action beats can trigger it.
- Occlusion, installation, transfer, interacting actors, directional effects, complex cameras or more than one scene require `previs` plus storyboard.
- Identity ambiguity requires an `identity_sheet`, verified against source images. This cannot replace operation evidence.

Operation evidence means legible verified source or reviewed generated imagery of the required interaction/state/result, not a product packshot, vague use-context label or a tiny hand inside a map. Use start/contact/end frames when one image cannot explain the transition. Inspect anatomy, left/right ownership, finger-target contact, occlusion, scale, fit and product identity. Do not force five visible fingers when some should be occluded; check plausible anatomy and continuity for the intended person. A generated operation frame that fails QC must not enter the reference set.

If the prompt adds actions absent from the shot rows, revise rows and reroute. Keep a hand ledger for risky shots: actor ID, left/right hand, task, start/end position, contact target, visible/occluded digits and release/exit. Specify what the inactive hand does. Preserve each person's anatomy across cuts. No new hand may appear merely to support a product.

## Plan contract

Use the existing backend, mode and selected_images fields, plus:

```json
{
  "routing_version": 2,
  "shot_rows_sha256": "actual file hash",
  "prompt_sha256": "actual model_prompt.md hash",
  "shot_assessments": [
    {"shot_id": "s01", "evidence": "Explain actual actions and reference gaps", "risks": {"wearing_fit": true, "finger_contact": false, "two_hand_interaction": false, "grip_change": false, "occlusion": false, "installation": false, "transfer": false, "multi_actor_interaction": false, "directional_effect": false, "complex_camera": false, "identity_ambiguity": false, "prior_anatomy_failure": false, "temporal_continuity": false, "mechanism_state": false, "material_change": false, "surface_contact": false, "contents_transfer": false, "interface_action": false}}
  ]
}
```

Each selected image retains absolute `path`, `sha256`, `qc: pass`, readable `role`; add `purposes` (one or more of identity, identity_sheet, operation, storyboard, previs), `covers_shots` (shot IDs), and a nonempty `visual_qc` observation. Purpose labels are assertions checked by visual review, not automated image recognition. One image may serve several purposes only when each is legible and reviewed. Record generated planning artifacts separately from the selected submission references if needed; no role may disappear silently at model formatting.

## Validation and recovery

`validate_reference_plan.py` fails missing assessments, stale hashes, unrecognized modes, underspecified risk flags, mismatched shot coverage, required purposes absent, or low-tier routing for high-risk actions. It validates declared data only; a human/agent must inspect images and verify the declared risks against the actual prompt. `prepare_request.py` separately enforces model limits and transport contracts.

After a hand/finger failure, flag affected shots `prior_anatomy_failure: true`, revise hand ledger and operation references before any authorized retry. Do not retry the same product-only plan with just a negative prompt. Do not silently simplify away the product's promised function.

For video QC, inspect contact start, peak occlusion, release and both sides of each cut; use short contiguous frame sequences around suspicious moments rather than only sparse contact sheets. Record shot ID, timestamp and failure evidence. Technical decoding and audio presence do not establish anatomical correctness. A pending or failed anatomy check cannot become a creative pass. References reduce ambiguity; they do not guarantee correct generation.
