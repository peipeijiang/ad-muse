# Local ASR profile

Use an OpenAI Whisper runtime that is already installed. `scripts/install_dependencies.py --check` reports the Python that can import `whisper` and which cached weights exist. Use `--verify-asr-hash` to check the official SHA-256 of large-v3-turbo.

Reference machine profile (verified on 2026-10-30; other machines will differ):

- Runtime: `/opt/anaconda3/bin/python`, OpenAI Whisper `20250625`.
- CLI: `/opt/anaconda3/bin/whisper`.
- Default: `~/.cache/whisper/large-v3-turbo.pt`, 1,617,941,637 bytes, official SHA-256 passed.
- Existing alternatives: `small.pt` and `base.pt`, official SHA-256 passed.
- `large-v3.pt` exists but failed official SHA-256; do not use it, repair it or download a replacement automatically.
- WhisperKit is not part of this profile. Use existing installations only.

## Invocation

```bash
<whisper-python> <this-skill-dir>/scripts/transcribe_local.py \
  /absolute/path/source.mp4 --language es \
  --output /absolute/path/reference-01/transcript.json
```

`<whisper-python>` is the interpreter reported by the dependency check, for example `/opt/anaconda3/bin/python` on the reference machine.

Omit `--language` when the source language is genuinely unknown. The source language is independent of the target market: an English reference for a Mexico output is transcribed in English, then adapted into es-MX downstream. Do not force es on that source.

The wrapper uses CPU/FP32, six threads, and word timestamps. It never downloads models: missing or corrupt weights fail before inference. Existing output is preserved; use a new output path for a deliberate recheck. Keep one accepted transcript path in the manifest with revisions linked as evidence rather than creating multiple competing transcriptions.

Output retains Whisper segments and word probabilities plus source/model hashes, runtime, device and execution time. Probabilities are model estimates, not calibrated guarantees. A successfully parsed result is not a human listening check. Do not overwrite uncertain ASR words with invented speech.

Primary source: [OpenAI Whisper](https://github.com/openai/whisper). Its speed comparisons are hardware-dependent; this local runtime has no implied A100 or Core ML speed.
