# Submission and QC checklist

## Before each paid request

- The product intake gate is passed and its hashes are current.
- `shot_rows.json` and any required storyboard/previs agree; omitted planning images have `not_required` decisions.
- `model_prompt.md` is the current prompt for this variant and satisfies the selected backend's prompt and duration contract.
- Every reference image has one role, a local path or verified URL, and a recorded hash.
- Backend, duration, ratio, resolution, locale, model, reference mode and reference count match the manifest. Omni Flash uses `omni-reference`, `16:9` or `9:16` and 720P: `omni_flash-10s` is exactly 10s with 1–7 references and `params` of only `aspect_ratio`/`images`; `omni-flash` is 4/6/8/10s with 1–3 references. AdMuse requires at least one verified reference even though the provider allows none for `omni_flash-10s`.
- Every reference's `transport` is recorded. If any is `data_url_compat`, a controlled smoke test on the current channel has passed before a formal batch (data URLs are not in the official Omni examples).
- `notify_url`, if used, is top-level, not inside `params`.
- The exact prompt hash and reference hashes are written before POST.
- The task is not already submitted under the same prompt/reference hash.

## After POST

Record the returned task ID immediately. For Omni, poll `GET https://api.lk888.ai/v1/media/status?task_id={task_id}` every 3–5 seconds. Check `is_final === true` first, then `state` (`pending`, `running`, `success`, `failed`); never branch on the Chinese display fields `status`/`status_group`. Treat a non-final task as active; never POST again just to check progress. Record the final `cost`, `refunded` state and output URL from the final response. A `failed` Omni task is refunded automatically; if the failure is a channel reference cap, reduce the reference plan with a recorded reason before any retry, never by silent slicing.

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
