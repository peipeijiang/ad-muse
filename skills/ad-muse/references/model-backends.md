# Model adapters

Default: MiniMax H3. Explicit alternative: Omni Flash, maximum 10 seconds per generation. Default Omni duration is 10 seconds. Do not silently carry over the H3 15-second default. An explicit longer target needs an agreed multi-clip plan or a brief adjustment before paid work.

## Shared artifacts, distinct formatting

Product facts, reference-video/ASR evidence, variant allocation, shot rows and physical constraints are shared. Only the final prompt and API fields depend on the selected model.

- H3: use `minimax-h3-creative-director` and its official full-reference/multishot rules. Save the actual submission text as `model_prompt.md`; a Chinese review translation can be displayed in chat without creating another paid prompt.
- Omni: write `model_prompt.md` from the accepted action draft. Use reference roles → style/product lock → timecoded shots → exact target-language dialogue and sound → concise physical/identity constraints. Keep the complete timeline within 10 seconds and the prompt within the existing local adapter's 4000-character budget. Revise content rather than truncating it. A useful 10-second template is 0–2 hook, 2–3 context change, 3–7 action/proof, 7–10 result/CTA; use a different structure when required by the reference.
- Generated storyboard/previs and identity sheets are optional for both routes. When included, describe them as planning references; forbid showing the board layout in the actual video. Omission requires a recorded reason, not an empty placeholder.

The old `product-ugc-pipeline/scripts/generate_videos_lk888.py` combines planning, required v2 storyboard/identity gates and prompt rewriting. Do **not** call its `process_variant` or command-line runner for the unified workflow: it would override the reviewed prompt and defeat the product-images-only route. Legacy standalone runs keep that behavior.

## Request serializer

`scripts/prepare_request.py` uses the existing LK888 field mapping without importing that old runner. It performs no upload, network request or paid submission. It reads the variant's canonical artifacts, verifies selected image hashes/QC, checks shot timing and model limits, and saves an exact request plus provenance.

```bash
python3 <this-skill-dir>/scripts/prepare_request.py \
  /absolute/run/variants/variant-01 --output /absolute/run/variants/variant-01/request.json
```

Input shapes:

```json
// brief.json (valid JSON without this comment)
{"model":"omni-flash","duration":10,"aspect_ratio":"9:16","resolution":"768p","locale":"es-MX"}
// shot_rows.json: one array; retain all creative fields alongside these times
[{"start_sec":0,"end_sec":2},{"start_sec":2,"end_sec":10}]
// reference_plan.json: selected image paths are absolute
{"backend":"omni-flash","mode":"product_images_only","selected_images":[{"path":"/absolute/product.jpg","role":"SKU front and mounting direction","sha256":"actual file hash","qc":"pass"}]}
```

The resolution value is an illustrative existing project value, not a capability guarantee. Check the current provider's supported resolution, duration choices, reference mode and price before any live submission. Do not fabricate accepted enum values.

| Model | Reference payload field | Local serializer envelope |
|---|---|---|
| `minimax-h3` | `params.image_url` | 4–15s, up to 9 images, prompt ≤7000 characters |
| `omni-flash` | `params.images` | ≤10s, up to 3 images, prompt ≤4000 characters |
| `omni_flash-10s` | `params.images` | exactly 10s; same conservative 3-image cap; duration/resolution omitted as in the existing fixed-duration adapter |

These mappings are grounded in the existing local adapter, not a new paid capability test. The legacy fixed-duration code permits seven images; this unified profile conservatively caps both Omni names at three until separately verified. Never truncate a selected reference list to fit a limit: revise the plan while preserving the required identity/direction evidence.

The serializer packages local images as data URLs. Check transport support and payload size before paid submission; if the provider requires URLs, use the approved upload path for the exact same image bytes and record the transport mapping. Never print base64 or credentials in status updates.

After structural validation, still review product identity, reference roles, source-video fidelity, dialogue duration and physical causality. Submit only `request.json.payload` through the approved provider with authorization for that batch, and record task ID immediately. Saving a request is not submission, nor a successful render.
