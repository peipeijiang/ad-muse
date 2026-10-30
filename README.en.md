[简体中文](README.md) · **English**

<p align="center"><img src="assets/banner.svg" alt="AdMuse: turn products and inspiration into video ads" width="100%"></p>

<p align="center">
  <a href="LICENSE"><img alt="License MIT" src="https://img.shields.io/github/license/peipeijiang/ad-muse?style=for-the-badge&color=8b5cf6"></a>
  <img alt="Agent Skill" src="https://img.shields.io/badge/Agent%20Skill-Codex%20%7C%20Claude%20Code-ec4899?style=for-the-badge">
  <img alt="Default backend MiniMax H3" src="https://img.shields.io/badge/default-MiniMax%20H3-f59e0b?style=for-the-badge">
  <img alt="Python 3" src="https://img.shields.io/badge/python-3-3776ab?style=for-the-badge&logo=python&logoColor=white">
  <img alt="Languages" src="https://img.shields.io/badge/docs-%E4%B8%AD%E6%96%87%20%7C%20English-10b981?style=for-the-badge">
</p>

> Turn a product link and reference videos into product videos with a faithful look, correct cause-and-effect action, and local QC.

AdMuse is an Agent Skill orchestration workflow; it does not render pixels itself. Before any paid generation, it breaks a video into four checkable planning artifacts: **shot plan, storyboard, white-mesh previs and action chain**. The final prompt is written only after they agree. It calls MiniMax H3 by default and Omni Flash (up to 10 seconds per clip) when you select it explicitly.

<p align="center"><img src="assets/planning-chain.en.svg" alt="Planning chain: shot rows → storyboard → white-mesh previs → action chain → cross-artifact gate" width="100%"></p>

## Highlights

Every step from reference video to final cut has a concrete artifact and a pass condition.

<p align="center"><img src="assets/highlights-1.en.svg" alt="Highlights 01–02: shot-by-shot reference breakdown, shot planning" width="100%"></p>
<p align="center"><img src="assets/highlights-2.en.svg" alt="Highlights 03–04: storyboard, white-mesh previs" width="100%"></p>
<p align="center"><img src="assets/highlights-3.en.svg" alt="Highlights 05–06: action chain, cross-artifact gate" width="100%"></p>
<p align="center"><img src="assets/highlights-4.en.svg" alt="Highlights 07–08: smart reference routing, paid-run safety and two-pass QC" width="100%"></p>

## Workflow

```mermaid
flowchart TD
  IN["Product URL / images<br/>optional: reference videos"]:::input
  G1{"Brief<br/>market · backend · duration · count"}:::gate
  HY["Reference breakdown<br/>hypit + local Whisper"]:::skill
  PUP["Product intake<br/>product-ugc-pipeline"]:::skill
  CSG["① Shot planning<br/>commerce-shot-grammar<br/>shot_rows.json"]:::skill
  RT{"Reference routing<br/>reference_plan.json"}:::gate
  SB["② Storyboard<br/>storyboard.png"]:::artifact
  PV["③ White-mesh previs<br/>previs.png"]:::artifact
  XQC{"Cross-artifact gate"}:::gate
  WVP["④ Action chain<br/>writing-video-prompts"]:::skill
  H3D["minimax-h3-creative-director<br/>final H3 prompt"]:::model
  OMF["Omni formatter<br/>≤10 s · ≤3 images"]:::model
  G2{"Paid-run approval"}:::gate
  SUB["prepare_request.py → LK888<br/>serial submit · poll same task"]:::tool
  QC["Local download · technical QC · creative QC"]:::tool
  OUT["downloads/*.mp4<br/>submission_manifest.json"]:::output

  IN --> G1
  G1 -->|with references| HY --> PUP
  G1 -->|no references| PUP
  PUP --> CSG --> RT
  RT -->|product / identity images| XQC
  RT -->|storyboard needed| SB
  SB -->|no spatial reference| XQC
  SB -->|spatial reference| PV --> XQC
  XQC -.mismatch: fix from upstream.-> CSG
  XQC --> WVP
  WVP -->|default| H3D --> G2
  WVP -->|explicit choice| OMF --> G2
  G2 --> SUB --> QC --> OUT
  QC -.failed and rework approved.-> WVP

  classDef input fill:#fef3c7,stroke:#d97706,color:#1f2937
  classDef skill fill:#ede9fe,stroke:#7c3aed,color:#1f2937
  classDef tool fill:#e0f2fe,stroke:#0284c7,color:#1f2937
  classDef model fill:#fce7f3,stroke:#db2777,color:#1f2937
  classDef gate fill:#fff7ed,stroke:#ea580c,color:#1f2937
  classDef artifact fill:#f1f5f9,stroke:#64748b,color:#1f2937
  classDef output fill:#dcfce7,stroke:#16a34a,color:#1f2937
```

| Stage | Owner | Output | Passes when |
|---|---|---|---|
| Brief | `ad-muse` | `pipeline_manifest.json` | Market and language, backend, duration, ratio and count are set |
| Reference breakdown (optional) | `hypit` + local Whisper | `reference_analysis.json`, `transcript.json` | Every shot has timing, camera language and evidence frames |
| Product intake | `product-ugc-pipeline` | `product_brief.json`, `product_reference_set/` | Look, structure, controls and supported states are backed by images or sources |
| Shot planning | `commerce-production-workflow` + `commerce-shot-grammar` | `shot_rows.json` | Contiguous timings; every shot has camera, contact point and before/after state |
| Reference routing | `ad-muse` | `reference_plan.json` | Every selected image has a role, hash and reason |
| Storyboard / previs (as needed) | `commerce-production-workflow` | `storyboard.png`, `previs.png` | Matches the shot table and passes the cross-artifact gate |
| Action chain | `writing-video-prompts` | `action_prompt_draft.md` | One main action per shot, visible causal order |
| Final prompt | `minimax-h3-creative-director` or Omni formatter | `model_prompt.md` | Duration, image count, length and image roles fit the backend |
| Submission | `prepare_request.py` → LK888 | `submission_manifest.json` | Paid run approved; one at a time; same task polled |
| Acceptance | `ad-muse` | `downloads/*.mp4`, `qc/` | Technical and creative QC judged separately |

**Reference-routing modes**

| Mode | When |
|---|---|
| `product_images_only` | Source images show the product clearly, one simple state, obvious action |
| `identity_plus_product` | Ambiguous geometry, several visible sides, or state-sensitive parts |
| `storyboard_plus_product` | Several meaningful shots, or a reveal/proof sequence text alone won't preserve |
| `full_spatial_reference` | Hand contact, installation, axis, light/air/spray direction or complex camera movement matters |

A generated identity image that changes the SKU, geometry, orientation or control layout is discarded in favor of the verified source images.

Reference-to-output allocation: with N references and M requested videos, each reference gets ⌊M/N⌋ outputs and the first M mod N references get one more; when M < N, only the first M are used. For example, 10 references and 20 videos means 2 per reference.

## Quick start

```bash
git clone https://github.com/peipeijiang/ad-muse.git
cd ad-muse
python3 install.py --check   # report only, install nothing
python3 install.py           # add missing skills, skip existing ones
```

Then invoke it in Codex or Claude Code:

```text
$ad-muse Make 5 Mexican-Spanish videos from this 1688 link, 15 s, 9:16, 768P.
Reference videos: https://www.tiktok.com/@xxx/video/123, https://www.tiktok.com/@yyy/video/456
```

Paid generation uses your own LK888/upDrama account, with the key supplied through the `LK888_API_KEY` environment variable. Product-image analysis is done directly by the current agent's multimodal model; no extra vision API or key is needed. Without paid-run approval, AdMuse stops at reviewable planning files, prompts and request files.

## Model backends

| Backend | Duration | Reference images | Prompt | When |
|---|---|---|---|---|
| `minimax-h3` | 4–15 s, 24 FPS | up to 9 | ≤7000 chars | Default |
| `omni-flash` / `omni_flash-10s` | ≤10 s | up to 3 | ≤4000 chars | Explicit choice |

Both backends share the same shot table, product brief and references; only the final prompt, reference selection and request envelope differ. If Omni Flash is selected with a 15-second request, AdMuse does not silently shorten it or switch models; it proposes a multi-clip plan or asks you to adjust the brief.

## Dependencies

`install.py` checks `~/.agents/skills` and then `~/.codex/skills`. Existing skills are always skipped and never overwritten; missing ones are installed into `~/.agents/skills`.

| Skill | Role | Source |
|---|---|---|
| `ad-muse` | Orchestration, reference routing, submission and acceptance | this repo |
| `commerce-production-workflow` | Production order, storyboard and previs, cross-artifact QC | this repo |
| `commerce-shot-grammar` | Axis, blocking, camera, contact and state | this repo |
| `product-ugc-pipeline` | Product scraping, asset manifest, product brief, identity references | [peipeijiang/product-ugc-pipeline](https://github.com/peipeijiang/product-ugc-pipeline) |
| `writing-video-prompts` | Model-neutral action and physics draft | [SupercmoHQ/superCMO-skills](https://github.com/SupercmoHQ/superCMO-skills) |
| `minimax-h3-*` (6) | H3 routing, reference/text/first-last-frame/multishot prompts and review | [unknowlei/minimax-h3-opencode-skills](https://github.com/unknowlei/minimax-h3-opencode-skills) |
| `h3-prompt-writing` | Official H3 prompt grammar | [MiniMax-AI/MiniMax-H3](https://github.com/MiniMax-AI/MiniMax-H3) |
| `hypit` | Reference-video download and analysis | [hypit-ai/hypit](https://github.com/hypit-ai/hypit) |

Local tools are checked, never installed: `git`, `ffmpeg` and `ffprobe` are required; the `hypit` CLI is used in reference-video mode (`npm install -g @hypit/hypit`); Whisper needs a Python that can `import whisper` and cached weights. Add `--verify-asr-hash` to check the official large-v3-turbo SHA-256, or `--json` for machine-readable output.

## License

[MIT](LICENSE). Third-party skill sources and licenses are listed in [NOTICE.md](NOTICE.md).
