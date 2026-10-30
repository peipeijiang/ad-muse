---
name: ad-muse
description: "AdMuse: produce product-faithful ecommerce videos from a product URL or image, optionally recreating supplied reference videos, through the default MiniMax H3 backend or an explicitly selected Omni Flash backend. Use one canonical product dossier, shot plan, optional storyboard/previs and model-specific final prompt, then submit, poll, download and QC each render."
license: MIT
metadata:
  version: "0.3.1"
  category: creative
  summary: "AdMuse · 广告缪斯 — from product evidence and reference inspiration to locally validated MiniMax H3 or Omni Flash videos."
---

# AdMuse · 广告缪斯

Use this skill for a product video that must end as a MiniMax H3 video by default, or an explicitly selected Omni Flash video, through LK888/upDrama, with the final MP4 saved locally and checked. It is an orchestration skill: it assigns one job to each existing skill and keeps one canonical artifact for each job.

## Dependency check

Before the first stage of a run, verify the companion skills and local tools without installing anything:

```bash
python3 <this-skill-dir>/scripts/install_dependencies.py --check
```

If a required skill is missing, report it and run the same script without `--check` only when the user has asked to install dependencies. The installer never overwrites an existing skill, and it never downloads Whisper or other model weights.

## Skill roles

Read the linked skill before executing its stage:

| Stage | Skill | Sole responsibility | Canonical output |
|---|---|---|---|
| Product intake | `product-ugc-pipeline` | Extract the complete source offer, analyze all product assets, build product facts, and create the canonical product reference set | `product_manifest.json`, `image_analysis.json`, `product_brief.json`, `product_reference_set/` |
| Reference-video intake | `hypit` plus local ASR | Download each supplied reference, read its complete audiovisual structure, extract timed speech, and write a clone blueprint | `reference_videos/<reference-id>/`, `reference_analysis.json`, `reference_transcript.json` |
| Production order | `commerce-production-workflow` | Enforce the order, approval gates, artifact provenance, and cross-artifact QC | `pipeline_manifest.json`, stage status and gate decisions |
| Shot planning | `commerce-shot-grammar` | Fill the shot rows with axis, blocking, camera, contact, state and movement decisions | `shot_rows.json` plus the storyboard and previs paths recorded in the manifest |
| Action prompt | `writing-video-prompts` | Turn the accepted shot rows into one model-neutral action/physics draft per clip | `action_prompt_draft.md` |
| Model formatting | `minimax-h3-creative-director` for H3, this skill’s Omni formatter for Omni Flash | Convert the accepted plan into exactly one backend-specific final prompt and reference list | `model_prompt.md` |
| Paid execution | this skill | Submit one request at a time, poll the same task, download the result and update the manifest | `submission_manifest.json`, `downloads/*.mp4` |
| QC | this skill with `ffmpeg`, `ffprobe`, sampled frames and local Whisper when speech matters | Verify technical validity, product identity, causal action, language and continuity | `qc/technical.json`, `qc/creative.json` |

Do not create a second product brief, second shot list, second storyboard, second previs, or second final prompt for the same variant. A downstream stage reads and annotates the upstream artifact instead of rewriting it.

## Backend routing

MiniMax H3 is the default backend. Omni Flash is an explicit alternative; selecting it does not create a second product brief, shot list, storyboard or previs.

Persist the normalized backend profile in `pipeline_manifest.json`, every variant and every submission row:

| Backend | Accepted model names | Duration contract | Reference/prompt adapter |
|---|---|---|---|
| `minimax-h3` | `minimax-h3` (record the provider alias when it differs) | 4–15 seconds | `minimax-h3-creative-director`; H3 reference router |
| `omni-flash` | `omni_flash-10s` (fixed 10s, 1–7 refs) or `omni-flash` (4/6/8/10s, 1–3 refs); both 16:9 or 9:16, 720P | **At most 10 seconds**; reject longer requests instead of silently truncating | This skill’s `omni-reference` request adapter |

Rules:

- If the user does not choose a backend, use `minimax-h3`.
- Resolution defaults are backend-specific: **Omni Flash is 720p**, while the MiniMax H3 profile defaults to **768P**. Never copy H3's `768P` into an Omni brief or request. `omni_flash-10s` is fixed 720P and its `params` carry only `aspect_ratio` and `images`; `omni-flash` selects the 720p baseline with `enable_upsample: false` and `enhance_prompt: false`. Neither Omni request sends a `resolution` field. Record `720p` as the intended output, and verify actual dimensions with `ffprobe` after download rather than treating a request setting as proof.
- Normalize aliases before the first paid request and record both requested and provider-returned model names.
- Omni Flash never inherits H3's 15-second allowance. An unspecified Omni duration defaults to 10 seconds. If 15 seconds was explicitly requested with Omni, never silently shorten it or switch the model: preserve 15 seconds as the deliverable target and plan multiple clips only if permitted by the brief; otherwise resolve this conflict before spending. If the user requested a 10-second adaptation, re-time shots and rewrite dialogue rather than mechanically accelerating them.
- Both backends consume the same accepted `shot_rows.json`, product brief and references, with storyboard/previs only when the route requires them. Only the final prompt, reference selection and API envelope are backend-specific.
- Store exactly one backend-specific prompt as `model_prompt.md`; do not write a second H3/Omni prompt for the same variant.

For `omni-flash`, read [model-backends.md](references/model-backends.md) and use this skill’s request adapter; do not call the legacy prompt-rebuilding submission flow. Select the fewest references that carry the required evidence (commonly one verified product image): at most seven for `omni_flash-10s`, at most three for `omni-flash`, in this order when each is needed: chronological storyboard, verified product identity/source image, then an operation or spatial reference. Some channels accept fewer images than the model limit (some only one); an over-limit task can fail with an automatic refund, after which reduce the plan with a recorded reason and retry. The provider allows zero images for `omni_flash-10s`, but AdMuse requires at least one verified product/identity reference; that is product policy, not an API limit. Omit a reference that is not needed or fails QC; never silently slice a reviewed set. Record selected roles, hashes and reasons in `reference_plan.json`.

## Reference-video mode

When the user supplies one or more reference-video links or files, run the reference branch before creative planning. Use the installed `/hypit` skill for downloading and reference understanding, but use its output as a creative specification for the later selected backend. Do not silently replace the deliverable with a Hypit render.

### Download and read each reference

For every link, assign a stable `reference_id` in input order. Use `hypit media prepare-fetch` once when needed, then:

```bash
hypit media fetch "<reference-url>" --to reference_videos/<reference-id>/source.mp4 --json
hypit media probe reference_videos/<reference-id>/source.mp4 --json
hypit media boundaries reference_videos/<reference-id>/source.mp4 --json
```

For a supplied local file, preserve it under the same directory and record the original path. Keep the source URL, local path, duration, dimensions, frame rate and audio presence. A download failure is recorded against that reference; do not substitute a different video or claim it was analyzed.

Use `hypit media frames`, `tile` or `tiles` around candidate boundaries and at the opening, product reveal, proof and closing. Mechanical boundaries are candidates, not editorial truth: confirm each cut from the frames and the whole video. Preserve source timecodes.

### Local ASR is part of the reference read

Use the user's **already installed** OpenAI Whisper runtime and cached weights. Do not install WhisperKit, MLX, WhisperX, faster-whisper or download new weights unless separately requested. Default to `large-v3-turbo`; choose `small` or `base` only when the user prioritizes speed over accuracy. Model availability means an existing file with the official SHA-256, not merely an installed CLI or a filename.

Read [local-asr.md](references/local-asr.md) for the verified local command. Use `scripts/transcribe_local.py` through the Python interpreter that already imports `whisper` (reported by `scripts/install_dependencies.py --check`): it checks weight integrity, loads only a local file, transcribes the original language, and preserves segments, words, probabilities and provenance in one `transcript.json`. This tested profile uses CPU/FP32 with six threads; Apple MPS availability alone does not establish Whisper compatibility.

`large-v3-turbo` is a practical multilingual default, not a guarantee of maximum accuracy. Full `large-v3` is an optional accuracy comparison only if its weights already pass verification; never auto-download it. The `626MB` WhisperKit variant is compressed Turbo, not full large-v3. Turbo is not trained for translation into English; preserve the original-language transcript and perform downstream text translation separately.

A local transcript is speech evidence, not ground truth or a sound-effect classifier. Preserve the raw ASR result; note uncertain words and manual corrections separately in the reference analysis. Review audio for music, ambience, effects and emphasis. Word timestamps are estimates, so inspect critical speech-to-cut alignment before using them as edit points.

### Required per-reference clone blueprint

Write one `reference_analysis.json` and a human-readable `reference_analysis.md` per reference. Each shot record must include:

```text
shot_id, start_sec, end_sec, duration_sec,
shot_size, aspect/framing, viewpoint/angle,
composition and subject placement,
visible product/object state,
primary action and result,
camera movement and speed,
focus/depth, lighting direction and palette,
cut/transition into the next shot,
spoken words and word-time range,
ambience, SFX, music and on-screen text,
what to preserve, what to replace, confidence/evidence paths
```

Also write a whole-piece reading: hook, argument or story, product reveal, proof, payoff, CTA, pacing pattern, recurring graphic system and the reason the reference holds attention. The result is a reusable creative blueprint, not a claim to have recovered the original prompt or source code.

Keep the distinction between a source **shot** and a generated **clip**. A generated clip may contain several cuts and location changes when the selected backend supports them. Split into separate generations only when duration, reference capacity or continuity requires it; do not create a paid generation for every source cut or scene change.

### Reference-to-output allocation

Let `N` be the number of reference videos and `M` the requested output count. Allocate variants deterministically in input order:

- `M = N`: one output for each reference;
- `M > N`: each reference receives `floor(M/N)` outputs, and the first `M mod N` references receive one extra;
- `M < N`: use the first `M` references and mark the unused references explicitly.

Each variant stores `reference_id`, `repeat_index`, `source_analysis_hash` and `product_variant_id`. Repeated outputs reuse the same reference blueprint unless the user explicitly asks for a creative variation; they may change the product, market, speaker, language or approved offer while retaining the source's chosen structure and pacing.

## Intelligent model reference routing

Before model formatting, produce one `reference_plan.json` per variant. It chooses the smallest reference set that can preserve the required identity and action. The router considers product-identity confidence, source-image coverage, number of product states, hand/contact complexity, directional effects, scene changes, camera complexity, reference storyboard quality and the selected backend's image limit.

Use these modes:

| Mode | Include | Choose when |
|---|---|---|
| `product_images_only` | Two to four verified product images, including a use-context image when available | Product identity is clear, the product stays in one simple state, the action is obvious, and no complex spatial or directional behavior must be copied; for Omni Flash, reduce this to the selected model's limit by plan revision, not slicing |
| `identity_plus_product` | Identity reference set plus the minimum verified source images | The product has ambiguous geometry, multiple visible sides, state-sensitive parts or the generated identity image is needed to keep the SKU stable; for Omni Flash, the selected set must still fit the model limit (7 for `omni_flash-10s`, 3 for `omni-flash`) |
| `storyboard_plus_product` | Accepted storyboard plus product images; identity set only if its gate requires it | The reference has several meaningful shots, fast but readable changes, or a product reveal/proof sequence that prompt text alone will not preserve |
| `full_spatial_reference` | Storyboard, previs and the minimum product/identity references | Hand-object contact, installation, axis, light/air/spray direction, multi-location movement or complex camera geometry materially affects the recreation; for Omni Flash, reduce this to the most informative references within the model limit |

The router must be conservative about adding references and conservative about omitting identity. If raw source images correctly show the SKU and the usage scene is simple, `product_images_only` is preferred. If a storyboard or previs is not needed, omit it. If a reference image is wrong, exclude it and keep the verified source image instead. Never exceed the selected backend's official image limit; record each selected image's role, path, hash and reason.

The final backend-specific prompt must name every selected image role explicitly. It must also say which source-video decisions are being preserved and which content is replaced with the user's product. Do not write vague instructions such as “use all references.”

## Boundary of `product-ugc-pipeline`

In this pipeline, `product-ugc-pipeline` runs only its product-intake portion:

```text
source extraction
→ complete asset manifest
→ image analysis
→ product brief and taxonomy
→ canonical product identity/reference images
→ product-intake QC
```

For the default H3 route, do not call its Omni Flash prompt or video submission steps. When the user explicitly selects Omni Flash, use this skill’s formatter and request serializer after the canonical shot plan and required-reference QC; do not rerun product intake or create parallel artifacts. The older all-in-one Omni scripts remain available for legacy projects that explicitly request that route.

The intake must preserve every source product image and its origin. Generate a clean product reference image or identity lock only when it remains faithful to the source. If the generated image changes the SKU, geometry, orientation, controls, label placement or material, keep the verified source images as the identity references and record the generated image as rejected.

## Canonical run folder

Create one run folder per product and batch. Use this layout; do not scatter copies across temporary folders:

```text
run/
├── reference_videos/                 # one downloaded source folder per reference
│   └── reference-01/
│       ├── source.mp4
│       ├── transcript.json
│       ├── boundaries.json
│       ├── frames/
│       └── reference_analysis.md
├── product_manifest.json
├── image_analysis.json
├── product_brief.json
├── product_reference_set/
│   ├── identity-lock.png             # optional, only when source images are insufficient
│   └── source/                       # exact source images, when needed
├── pipeline_manifest.json            # one state record for the whole run
├── variants/
│   └── variant-01/
│       ├── brief.json
│       ├── reference_plan.json
│       ├── shot_rows.json
│       ├── storyboard.png           # optional, route-dependent
│       ├── previs.png               # optional, route-dependent
│       ├── action_prompt_draft.md
│       ├── model_prompt.md
│       ├── submission.json
│       ├── downloads/
│       └── qc/
└── submission_manifest.json           # one row per paid task, updated in place
```

`pipeline_manifest.json` records stage status and provenance. `submission_manifest.json` records paid-task facts. Do not make a separate status file for every poll.

## Execution order

### 1. Resolve the brief once

Record product source, target market and spoken locale, backend/model, duration, ratio, resolution, number of variants, and whether the user wants a preview or paid generation. Reuse already settled choices. If the user has said to decide missing creative choices, select and record a coherent option instead of reopening the same question.

For MiniMax H3 online generation, keep the effective duration between 4 and 15 seconds, 24 FPS, and the final English prompt at or below 7000 characters. For Omni Flash, use `omni_flash-10s` (exactly 10 seconds) or `omni-flash` (4, 6, 8 or 10 seconds), ratio 16:9 or 9:16, and the `omni-reference` request envelope. Record 720p as its resolution; neither Omni request sends a `resolution` parameter. Default only when the brief leaves it open: `minimax-h3`, 15 seconds, 9:16, H3 768P or Omni Flash 720p, and Mexican Spanish when the market is Mexico.

### 2. Run reference-video intake when present

If the brief includes reference links or files, complete the reference-video branch above before writing the product creative plan. If there are no references, record `reference_mode: none` and continue.

### 3. Run product intake

Read and follow `product-ugc-pipeline/SKILL.md`, but stop after its source-completeness, product-cognition, identity-reference and intake-QC gates. The intake handoff must include:

- complete `product_manifest.json` with source URL and source surface for every asset;
- `image_analysis.json` covering exactly the manifest image set;
- `product_brief.json` with verified appearance, dimensions when known, mechanism, supported states, use and misuse constraints;
- a canonical product reference set with file hashes and roles;
- an explicit list of unknown facts and rejected generated references.

Do not infer a feature from a marketing phrase when the image or source does not support it.

### 4. Build one production plan

Use `commerce-production-workflow` as the outer production order and `commerce-shot-grammar` as its internal shot-planning method. The single plan must contain:

- one `shot_rows.json` with contiguous timings that sum to the target duration;
- one spatial/white-mesh previs artifact only when contact/direction/geometry risk requires it, derived from the structured shot rows;
- one chronological storyboard artifact only if `reference_plan.json` requires it, derived from the accepted spatial previs;
- one cross-artifact QC result.

Create the reference plan before generating extra images, and refine it after QC without duplicating it. Omitted identity/storyboard/previs outputs are recorded as `not_required` with a reason; they need no placeholder file and are not failed gates. This orchestrator’s optional-artifact contract takes precedence over mandatory image-generation steps in the component skills. The shot rows are the source of truth for any generated planning images. `commerce-shot-grammar` supplies axis, blocking, camera, contact and state decisions; it must not create an independent competing shot table. Establish the previs from those rows first; derive the storyboard from the accepted previs. The previs is for space and contact; the storyboard is for chronological visual beats. Keep their roles separate.

For each beat, record: start/end time, shot size, camera position and movement, product orientation, hand ownership and contact point, product state before/after, environment anchors, lighting direction, proof purpose, and spoken line. A product action must show a causal chain such as `hand contacts button → button is pressed → the light emits from its lamp face → the illuminated area lies in front of the lamp axis`.

Run the cross-artifact gate before writing a prompt. Product identity, hand, scene, lighting direction, axis, camera side, state transition, ratio and action order must agree. If they do not, revise the dependent artifact from the accepted one; never reconcile a mismatch by inventing a third state.

### 5. Draft actions and physical constraints

Use `writing-video-prompts` on the accepted shot rows and the actual storyboard/previs observations. Treat this as an action and physics draft, not the final backend schema. It must contain one primary moving action per beat, a visible start/process/result, physically possible contact and camera motion, exact beat timings, sound events and compact failure constraints.

For products with directional output, state the source and receiving geometry explicitly. For a lamp: the lamp face is the only emission point; the beam axis follows the lamp face; the illuminated patch is on a surface in front of that axis; pressing the control precedes illumination; no independent glow appears behind or beside the lamp. Generalize the same rule to fans, sprays, screens, magnets and other directional mechanisms.

Store only one `action_prompt_draft.md`. Do not submit it directly to either backend.

### 6. Produce the backend-specific final prompt

For `minimax-h3`, use `minimax-h3-creative-director` as the mandatory H3 entrypoint. Read its required official H3 references and pass:

- the settled shot plan;
- the action/physics draft;
- the product reference set with an explicit role for every image;
- the exact spoken script and locale;
- the target duration, ratio and resolution;
- the preservation and failure constraints.

When a reference blueprint exists, create `reference_plan.json` first and pass its selected roles unchanged. Preserve the reference's shot order, timing relationships, cut grammar, camera language, audio-to-picture relationships and visible text only where the user asked to retain them; replace the source product, claims, speaker or language according to the brief.

Because product images are reusable identity references, use the H3 full-reference route unless the user explicitly declares literal boundary-only frames with no identity or reusable reference role. If the video has intentional cuts, carry the confirmed shot plan into the H3 multishot route.

For `omni-flash`, read [model-backends.md](references/model-backends.md). Format the action draft as reference roles, global appearance/style, timed shots, exact dialogue/sound and product/physics constraints. Serialize only the selected and reviewed images into one `omni-reference` request, within the model limit (1–7 for `omni_flash-10s`, 1–3 for `omni-flash`). Simple products may use original product images alone. The prompt must fit the 0–10 second timeline, state the target language and sound/dialogue, and explicitly forbid reproducing the storyboard grid.

Write exactly one `model_prompt.md` for either branch. Before submission, check the selected backend envelope: H3 is 4–15 seconds and 24 FPS; Omni Flash is at most 10 seconds and its provider-supported frame/ratio settings. In both branches check prompt length, image count, role labels, timing sum, dialogue fit, sound section, and no contradiction between cuts, keyframes, references and audio. Keep the product identity reference order stable across variants.

### 7. Submit serially through LK888

Use `scripts/prepare_request.py` to prepare and structurally validate the selected backend request as described in [model-backends.md](references/model-backends.md). Then use the approved LK888/upDrama submission path already configured in the project, sending the exact payload (Omni: `POST https://api.lk888.ai/v1/media/generate`; top level `model`/`prompt`/`params`, optional top-level `notify_url`). Reference images go as provider https URLs when the plan has them; otherwise the serializer's data URL is an unverified compatibility path that needs one authorized smoke test per channel before a formal batch. The serializer does not itself submit. Do not silently switch provider, model or reference mode. Create one `submission.json` and one row in `submission_manifest.json` before each POST, including:

```text
variant_id, prompt_sha256, reference_paths_and_sha256,
backend, model, reference_mode, duration, aspect_ratio, resolution, locale,
submitted_at, task_id, state, cost, refunded,
remote_url, local_path, technical_qc, creative_qc
```

Submit one variant at a time. After each request, record the returned task ID and any reported charge; reconcile final cost/refund when the same task reaches a final state. Do not label an estimate or missing cost as actual final cost. A queued response is not completion. If the POST outcome is ambiguous, first inspect the known task/status and manifest; do not create a possible duplicate. If the balance, model, reference count, cost or provider response does not match the manifest, stop and report the mismatch.

### 8. Poll and download

Poll the exact task ID until it is final. For Omni, call `GET https://api.lk888.ai/v1/media/status?task_id={task_id}` every 3–5 seconds; check `is_final === true` first, then `state` (`pending`/`running`/`success`/`failed`). Never branch on the Chinese display fields `status` or `status_group`. A `failed` task is already refunded automatically; record it. Never submit a replacement while the task is pending. When a final output URL is available, download to a `.part` file, validate the file, then atomically rename it to the final `.mp4`. Preserve the task response, output URL and SHA-256 in the manifest.

### 9. Run two QC passes

Technical QC checks a real playable MP4, codec, duration, dimensions, frame rate, audio presence and file hash. Creative QC samples the opening, action, proof and closing frames and checks:

- the exact SKU, silhouette, material, controls and orientation;
- the product/hand/scene continuity and causal action order;
- the correct origin, direction and receiving surface of light or other directional effects;
- no duplicate product, impossible attachment, teleport, extra hand, unsupported feature, invented label or wrong locale;
- spoken language, timing, intelligibility and whether the product is actually shown doing the claimed action.

Use `pass`, `fail`, `needs_review` or `error` with evidence. Technical success never implies creative acceptance. If a clip fails, preserve it and report the failed check; rerender only with explicit authorization or when the user already authorized a correction batch.

## Handoff contract

At every handoff, state the canonical artifact path, revision/hash, status and next stage. A stage is complete only when its artifact exists and its gate is recorded. The final response must separate:

- submitted count;
- remote-final count;
- locally downloaded count;
- technical-QC pass count;
- creative-QC pass / needs-review count;
- local paths and any task IDs needing follow-up.

This separation prevents a successful API response, a downloaded file and an accepted creative from being reported as the same state.

## References

- [local-asr.md](references/local-asr.md) — existing local Whisper runtime, verified weights and offline invocation.
- [model-backends.md](references/model-backends.md) — model-specific formatting and dry-run request serialization.

- [artifact-contract.md](references/artifact-contract.md) — canonical artifact names, ownership and state transitions.
- [reference-video-cloning.md](references/reference-video-cloning.md) — source download, local ASR, shot records and reference routing schema.
- [physical-causality.md](references/physical-causality.md) — compact geometry and action constraints for commerce products.
- [submission-qc.md](references/submission-qc.md) — serial billing, polling, download and QC checklist.
