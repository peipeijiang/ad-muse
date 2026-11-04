# Storyboard and spatial previs layout — v2.0

## Visual direction

Use a black-and-white storyboard and a grayscale white/clay-model spatial map. Favor readable volumes, sparse contours and restrained shading. Do not substitute colored beauty renders, polished advertising images or a dense decorative wireframe for planning artifacts.

Combine a dominant scene map, a product/legend sidebar and short camera-side explanations. These are adaptable layout roles, not a required number of scenes or shots. Fit the sheet to the current story: a single tabletop demonstration needs no second location; multi-location stories may need separated maps or multiple sheets. Never inherit camera IDs, actor positions or product dimensions from a previous campaign.

## Storyboard

Default to a six-panel layout: three columns by two rows, ordered left to right and top to bottom. Change the panel count if explicitly requested or necessary to preserve the story’s essential beats; record the reason.

Show chronological composition and action with stable shot IDs. Follow the approved storyboard and creative brief for the opening Hook. Hooks may be a problem, result reveal, demonstration, dialogue, reaction, comparison, action or audio/text-led opening; no Hook type or location is mandatory. Preserve its actual composition and timing. The spatial map inherits only the environments, actors, props and actions that appear in that storyboard, without introducing a pickup, rush, crowd or product close-up by default. If the Hook exists only in speech/text, retain that information in the shot rows rather than inventing spatial action. Preserve grip, product face, state and transition. Lay out real target-ratio panels; a square panel marked “9:16” fails. Keep readable captions outside the image areas.

Generate this board through the LK888/upDrama media task with `tt-image-2.5`; record the model, task ID, params, prompt hash and output hash.

## White-model board

Use a landscape sheet as a practical default; the video frame ratio is a separate property. Starting layout proportions are flexible, not pixel requirements:

- Main spatial map about 60% of the whole sheet: elevated oblique/cutaway views with recognizable scene anchors. Separate locations clearly and connect them with CUT labels, not physical walking paths across unrelated sets.
- Right product/legend strip about 15–20%: verified silhouette/front/back and scale cue, plus only symbols actually used. Multiple product views must be labeled as views of ONE unit. Do not invent unavailable reverse details.
- Bottom compact camera-card strip about 20–25%: shot ID, camera station, shot size/view direction, movement and critical action. Keep it subordinate to the spatial map. Text cards are the default; add a few simplified grayscale camera-view previews when they resolve Hook framing, hand contact, product face or another concrete ambiguity. Do not automatically regenerate every storyboard panel here. Existing storyboard crops may be reused as explicitly labeled references, not passed off as new camera renders. Follow the approved visual layout direction: 07 for the dominant spatial map, 41 for the product/legend sidebar and 30 for concise camera-side descriptions. These are layout cues, not authoritative camera IDs or product facts.

Place short camera descriptions near the relevant stations as well as matching IDs in cards. Each camera station has a unique ID; shared stations may list multiple shot IDs. Show viewing direction and schematic field of view where useful, distinguish camera movement from actor/product motion, and mark the relevant axis. Do not attach decorative camera icons without a legible target.

Use one solid actor per person per scene state. For sequential positions use labeled ghosts or separated stages, so a single host is never mistaken for several people. Mark grip/contact, placement and release for actions where these matter. A product close-up requires its actual hand/product state, not just an arrow toward a table.

## Product scale

Read SKU, unit count, silhouette, front/back, dimensions, material and operating states from the current product dossier and verified identity references. Never hardcode a previous product's size, color, number of parts or hand-size comparison into the reusable workflow. Unknown dimensions stay unknown.

For handheld products, compare product and hand on the same depth plane and avoid foreground enlargement; a hand is an approximate visual cue, not a ruler. For other scales, use an appropriate verified reference (body, furniture, mounting surface or environment). Do not require hands or palm-sized staging for every product. Label enlarged sidebar views as enlarged and keep in-scene scale consistent with the dossier. Multiple views do not imply multiple physical units.

## Fast QC and revision

1. Inspect storyboard first: Hook rendered, panel ratio, product/hand consistency, action order, and generation provenance uses `tt-image-2.5`.
2. Inspect spatial board: dominant map, same locations, unique IDs, readable target directions, actor stages, product scale cue and contact/release; verify generation provenance uses `tt-image-2.5`.
3. Check each shot across rows, storyboard, map and bottom cards. Fix text/IDs with overlays when possible; regenerate only when composition/staging needs it. Any upstream edit invalidates affected downstream QC.
4. Record `visual_concept_check`, `measured_geometry_check` and `user_acceptance` separately as pass/fail/not_verified/pending with reasons. Schematics do not validate real lens FOV, occlusion, collisions or exact size. Framing previews must use actual target aspect ratio if claimed as frame checks.
5. Retain prompts, task IDs, inputs, revisions and costs if available. Do not rerun paid generation solely to improve an easily editable label.

## Method reference

AI Previs Director: https://github.com/ddokkang2/ai-previs-director-skill , inspected commit 09adade92c0eeddcaca1ddd3e8dcba25f95faec8. Adopt the general shared Master Shot Data principle: one set of shot IDs and scene/action/camera data informs all artifacts. This local guide is independently written; no upstream code or prompt text is copied. Original Yingce reference snapshots remain historical source material.
