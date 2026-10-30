# Submission and QC checklist

## Before each paid request

- The product intake gate is passed and its hashes are current.
- `shot_rows.json` and any required storyboard/previs agree; omitted planning images have `not_required` decisions.
- `model_prompt.md` is the current prompt for this variant and satisfies the selected backend's prompt and duration contract.
- Every reference image has one role, a local path or verified URL, and a recorded hash.
- Backend, duration, ratio, resolution, locale, model, reference mode and reference count match the manifest. Omni Flash is at most 10 seconds and uses `omni-reference`.
- The exact prompt hash and reference hashes are written before POST.
- The task is not already submitted under the same prompt/reference hash.

## After POST

Record the returned task ID immediately. Treat `pending` or `running` as an active task. Poll that ID; never POST again just to check progress. Record the final `cost`, `refunded` state and output URL from the final response.

## Download

Download the output into `downloads/<name>.mp4.part`, validate it, then rename atomically. Keep the original URL and task response. A failed download is a delivery problem, not permission to submit a duplicate task.

## Technical QC

Check with `ffprobe` or an equivalent media inspector:

- MP4 is readable;
- video stream exists;
- dimensions match the requested ratio and resolution within the provider's declared output;
- duration is within the requested tolerance;
- frame rate and audio stream are present as requested;
- final file hash is recorded.

## Creative QC

Sample frames and, where speech matters, sample audio/transcription. Record evidence for product identity, action causality, physical orientation, lighting direction, language, continuity and unsupported claims. Use `pass`, `fail`, `needs_review` or `error`; never convert missing evidence into a pass.
