# Model adapters

Default: MiniMax H3. Explicit alternative: Omni Flash, maximum 10 seconds per generation. Default Omni duration is 10 seconds. Do not silently carry over the H3 15-second default. An explicit longer target needs an agreed multi-clip plan or a brief adjustment before paid work.

## Shared artifacts, distinct formatting

Product facts, reference-video/ASR evidence, variant allocation, shot rows and physical constraints are shared. Only the final prompt and API fields depend on the selected model.

- H3: use `minimax-h3-creative-director` and its official full-reference/multishot rules. Save the actual submission text as `model_prompt.md`; a Chinese review translation can be displayed in chat without creating another paid prompt.
- Omni: write `model_prompt.md` from the accepted action draft. Use reference roles → style/product lock → timecoded shots → exact target-language dialogue and sound → concise physical/identity constraints. Keep the complete timeline within 10 seconds (exactly 10 for `omni_flash-10s`) and the prompt within the local adapter's 4000-character budget. Revise content rather than truncating it. A useful 10-second template is 0–2 hook, 2–3 context change, 3–7 action/proof, 7–10 result/CTA; use a different structure when required by the reference.
- Generated storyboard/previs and identity sheets are optional for both routes. When included, describe them as planning references; forbid showing the board layout in the actual video. Omission requires a recorded reason, not an empty placeholder.

The old `product-ugc-pipeline/scripts/generate_videos_lk888.py` combines planning, required v2 storyboard/identity gates and prompt rewriting. Do **not** call its `process_variant` or command-line runner for the unified workflow: it would override the reviewed prompt and defeat the product-images-only route. Legacy standalone runs keep that behavior.

## Request serializer

`scripts/prepare_request.py` uses the LK888 field mapping below without importing that old runner. It performs no upload, network request or paid submission. It reads the variant's canonical artifacts, verifies selected image hashes/QC, checks shot timing and model limits, and saves an exact request plus provenance.

```bash
python3 <this-skill-dir>/scripts/prepare_request.py \
  /absolute/run/variants/variant-01 --output /absolute/run/variants/variant-01/request.json
```

Input shapes:

```json
// brief.json (valid JSON without this comment)
{"model":"omni-flash","duration":10,"aspect_ratio":"9:16","resolution":"720p","locale":"es-MX"}
// shot_rows.json: one array; retain all creative fields alongside these times
[{"start_sec":0,"end_sec":2},{"start_sec":2,"end_sec":10}]
// reference_plan.json: selected image paths are absolute
{"backend":"omni-flash","mode":"product_images_only","selected_images":[{"path":"/absolute/product.jpg","role":"SKU front and mounting direction","sha256":"actual file hash","qc":"pass"}]}
```

Optional extras: a `selected_images[]` entry may carry `"url":"https://..."` (the provider-hosted copy of the same bytes as `path`); `brief.json` may carry `"notify_url":"https://..."` for Omni models.

### LK888 Omni Flash endpoints and envelope

- Create: `POST https://api.lk888.ai/v1/media/generate`
- Status: `GET https://api.lk888.ai/v1/media/status?task_id={task_id}`
- Request top level is exactly `model`, `prompt`, `params`, plus optional `notify_url`. `notify_url` is a top-level field and must never be placed inside `params`.

| Model | Duration | Ratio | Output | `params` sent | Provider reference limit | AdMuse requirement |
|---|---|---|---|---|---|---|
| `omni_flash-10s` | fixed 10s | `16:9` or `9:16` | fixed 720P | `aspect_ratio`, `images` only | 0–7 images (0 = text-to-video) | 1–7 verified references |
| `omni-flash` | 4, 6, 8 or 10s | `16:9` or `9:16` | 720P baseline | `aspect_ratio`, `images`, `duration`, `enable_upsample: false`, `enhance_prompt: false` | up to 3 images | 1–3 verified references |
| `minimax-h3` | 4–15s | per H3 profile | explicit resolution (default 768P) | `aspect_ratio`, `image_url`, `duration`, `resolution` | 9 images | 1–9 verified references |

For `omni_flash-10s`, never send `duration`, `resolution`, `enable_upsample` or `enhance_prompt`; the model name itself fixes 10 seconds and 720P. For `omni-flash`, never send `resolution`; `enable_upsample: false` keeps the 720P baseline and `enhance_prompt: false` keeps the reviewed prompt unchanged. Both Omni models keep the prompt within the local 4000-character budget. Reject a non-720p Omni brief instead of silently changing it, and verify actual encoded dimensions with `ffprobe` after download. Both Omni models use `backend: "omni-flash"` in `reference_plan.json`; the exact model lives in `brief.json`.

**Zero images is a provider capability, not an AdMuse option.** The provider accepts `omni_flash-10s` without references (text-to-video). AdMuse is a product-fidelity workflow, so the serializer requires at least one hash/QC-verified product or identity reference. Do not describe this policy as an API limit.

**Channel-level image caps.** The 7-image maximum for `omni_flash-10s` is the model limit; some upstream channels accept fewer images (some only 1). An over-limit task can fail and is automatically refunded. For product fidelity, send the minimum references that carry the required identity and direction evidence (commonly 1), up to 7. If a task fails and is refunded for reference count, revise `reference_plan.json` to fewer images with a recorded reason, rebuild the request and retry. Never slice a reviewed reference set silently, in the serializer or at submit time.

### Reference transport and provenance

The official Omni examples show `params.images` as https URLs. Data URLs (`data:image/...;base64,...`) are not shown in the official documentation; they may work, but that is unverified. The serializer therefore:

- sends the entry's `url` when present (must be absolute http/https) and records `transport: "provider_url"`, `url_host` and `url_sha256`;
- otherwise sends a data URL built from the local file and records `transport: "data_url_compat"`;
- always reads the local `path`, checks its `sha256`, `role` and `qc: "pass"`, and records `path` and `sha256` in provenance, so a URL is accepted only as a copy of verified bytes. Upload the exact same bytes; a re-encoded upload is a different reference.

When provenance shows `data_url_smoke_test_required: true`, run one controlled, explicitly authorized smoke test on the current channel before any formal batch, and record the task ID and outcome. The H3 branch keeps its existing data-URL behavior (`transport: "data_url"`) and ignores `url`. Never print base64 or credentials in status updates.

### Status polling

Poll `GET .../v1/media/status?task_id=...` every 3–5 seconds. Decide with `is_final` first: only when `is_final === true` is the task done; then read `state`. `state` is one of `pending`, `running`, `success`, `failed`. `status` and `status_group` are Chinese display strings and must never drive business logic. A `failed` task has already been refunded automatically; record `refunded` from the response and do not re-POST the same request to "check" progress.

These mappings follow the current provider documentation; they are not proven by a paid capability test in this skill. Recheck provider capabilities and pricing before live submission.

After structural validation, still review product identity, reference roles, source-video fidelity, dialogue duration and physical causality. Submit only `request.json.payload` through the approved provider with authorization for that batch, and record task ID immediately. Saving a request is not submission, nor a successful render.
