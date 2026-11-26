# Reference-video cloning contract

This branch turns a supplied video into an evidence-bounded creative blueprint for a later H3 or Omni Flash render.

## Source evidence

Keep the original URL or local path, the downloaded source, `ffprobe`/Hypit metadata, candidate cut boundaries, extracted frames or grids used as evidence, and the transcript when speech fidelity applies. Reuse the source analysis across variants. Record the adaptation in the existing shot rows and reference plan. Preserve target-model timing and record the reason for each changed, merged, or omitted source cut. Temporary contact sheets need no individual registration. Every observation in the analysis should point to a source time and, where useful, an evidence file.

## Fit the target duration before drawing

Keep the confirmed source cut order and as many meaningful cut points as the target allows. If the source exceeds the selected duration, retime the cut map before writing the action draft or drawing the board: H3 supports 4–15 seconds; Omni Flash supports a fixed 10 seconds or the selected 4/6/8/10-second profile. Shorten holds and redundant bridges first. Preserve the hook, readable action and its visible proof, intelligible required speech, and the closing beat. Merge or drop lower-priority cuts only when needed; record the source shot/time → target shot/time mapping and the reason in the existing shot rows or reference plan. Do not silently truncate the request or compress all shots uniformly. Use the resulting target beats to pick six versus nine readable storyboard cells only if the image route needs a board; a source cut does not require its own cell. Keep timestamps in the mapping, not on the board.

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

The example above shows the base fields only; new submissions must also include the current versioned assessments, hashes, purposes and coverage required by [reference-routing.md](reference-routing.md). Apply that router even without source videos. If the provider rejects a required role or exceeds a limit, revise the shot/reference plan and revalidate; never silently remove required evidence.
