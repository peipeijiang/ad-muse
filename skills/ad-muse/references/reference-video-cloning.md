# Reference-video cloning contract

This branch turns a supplied video into an evidence-bounded creative blueprint for a later H3 or Omni Flash render.

## Source evidence

Keep the original URL or local path, the downloaded source, `ffprobe`/Hypit metadata, candidate cut boundaries, extracted frames or grids, and the transcript. Every observation in the analysis should point to a source time and, where useful, an evidence file.

## Shot record

Use one record for each editorial shot, not each generated clip. Required fields:

```json
{
  "shot_id": "r01-s03",
  "start_sec": 4.2,
  "end_sec": 6.8,
  "shot_size": "medium close-up",
  "viewpoint": "eye-level three-quarter front",
  "composition": "subject right of frame, product enters from lower left",
  "product_state": "held closed, front face toward camera",
  "action": "hand lifts the product and turns it toward the lens",
  "camera": "short handheld push-in",
  "lighting": "cool overhead key from camera-left, soft shadow to rear-right",
  "transition_out": "hard cut on the turn",
  "speech": {"text": "...", "start_sec": 4.35, "end_sec": 5.9},
  "sound": ["room tone", "plastic click"],
  "preserve": ["timing", "push-in", "hard cut"],
  "replace": ["product", "spoken claims"],
  "evidence": ["frames/004.2.jpg", "frames/006.8.jpg"],
  "confidence": "high"
}
```

Do not claim to know the source model's hidden prompt. Describe only visible and audible choices, then write an adaptation decision for the user's product.

## Local speech evidence

The transcript should preserve segments and words with source timestamps, detected language, model, backend and confidence. Keep an `[unclear]` token where the local model cannot establish the wording. Use the transcript to align cuts, captions, product reveals and emphasis. Inspect the source audio separately for music and effects; ASR is not a sound-effect classifier.

## Reference plan schema

`reference_plan.json` is the routing result for one output variant:

```json
{
  "reference_id": "reference-01",
  "repeat_index": 1,
  "mode": "full_spatial_reference",
  "selected_images": [
    {"path": "product_reference_set/identity-lock.png", "role": "SKU identity", "sha256": "..."},
    {"path": "variants/variant-01/storyboard.png", "role": "chronological shot map", "sha256": "..."},
    {"path": "variants/variant-01/previs.png", "role": "spatial and contact geometry", "sha256": "..."}
  ],
  "omitted_images": [],
  "reasons": ["installation has a handoff and a directional light proof"],
  "backend": "minimax-h3",
  "image_count": 3,
  "source_analysis_sha256": "..."
}
```

The router must be deterministic from the evidence and must fit the selected backend reference limit. A downstream prompt can use fewer images than the plan when a provider rejects a role, but it must record the change and rerun the role/limit check.
