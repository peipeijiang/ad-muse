[简体中文](README.md) · **English**

<p align="center"><img src="assets/banner.svg" alt="AdMuse: turn products and inspiration into video ads" width="100%"></p>

<p align="center">
  <a href="LICENSE"><img alt="License MIT" src="https://img.shields.io/github/license/peipeijiang/ad-muse?style=for-the-badge&color=8b5cf6"></a>
  <img alt="Agent Skill" src="https://img.shields.io/badge/Agent%20Skill-Codex%20%7C%20Claude%20Code-ec4899?style=for-the-badge">
  <img alt="Default backend MiniMax H3" src="https://img.shields.io/badge/default-MiniMax%20H3-f59e0b?style=for-the-badge">
  <img alt="Python 3" src="https://img.shields.io/badge/python-3-3776ab?style=for-the-badge&logo=python&logoColor=white">
  <img alt="Languages" src="https://img.shields.io/badge/docs-%E4%B8%AD%E6%96%87%20%7C%20English-10b981?style=for-the-badge">
</p>

AdMuse is an Agent Skill orchestration workflow. It routes a product link and optional reference videos through a set of single-purpose skills, producing 9:16 product videos with a faithful product look and correct cause-and-effect actions, then downloads and checks each render locally.

It is not a video model itself. It calls MiniMax H3 by default and Omni Flash (up to 10 seconds per clip) when you ask for it explicitly.

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

Paid generation uses your own LK888/upDrama account, with keys supplied through environment variables (`LK888_API_KEY`; product-image analysis uses `LAOZHANG_API_KEY`). Without paid-run approval, AdMuse stops at reviewable prompts and request files.

## Workflow

```mermaid
flowchart TD
  IN["Product URL / images<br/>optional: reference videos"]:::input
  PUP["product-ugc-pipeline<br/>product intake only"]:::skill
  HY["hypit<br/>fetch · probe · cuts · frames"]:::skill
  ASR["Local Whisper<br/>large-v3-turbo"]:::tool
  BP["Shot-by-shot clone blueprint<br/>reference_analysis"]:::artifact
  G1{"Human gate<br/>market · duration · count"}:::gate
  CPW["commerce-production-workflow<br/>order and gates"]:::skill
  CSG["commerce-shot-grammar<br/>shot_rows.json"]:::skill
  RT{"Reference router<br/>reference_plan.json"}:::gate
  WVP["writing-video-prompts<br/>action and physics draft"]:::skill
  H3D["minimax-h3-creative-director<br/>final H3 prompt"]:::model
  OMF["Omni formatter<br/>≤10 s · ≤3 images"]:::model
  G2{"Paid-run approval"}:::gate
  SUB["prepare_request.py → LK888<br/>serial submit · poll same task"]:::tool
  QC["Local download · technical QC · creative QC"]:::tool
  OUT["downloads/*.mp4<br/>submission_manifest.json"]:::output

  IN --> PUP
  IN -.reference videos.-> HY --> ASR --> BP
  PUP --> G1
  BP --> G1
  G1 --> CPW --> CSG --> RT --> WVP
  WVP -->|default| H3D --> G2
  WVP -->|explicit| OMF --> G2
  G2 --> SUB --> QC --> OUT
  QC -.fail + authorized rerender.-> WVP

  JD["judian-skills shot grammar"]:::ref
  YC["Yingce short-drama workflow"]:::ref
  JD -. adapted from .-> CSG
  YC -. adapted from .-> CPW

  classDef input fill:#fef3c7,stroke:#d97706,color:#1f2937
  classDef skill fill:#ede9fe,stroke:#7c3aed,color:#1f2937
  classDef tool fill:#e0f2fe,stroke:#0284c7,color:#1f2937
  classDef model fill:#fce7f3,stroke:#db2777,color:#1f2937
  classDef gate fill:#fff7ed,stroke:#ea580c,color:#1f2937
  classDef artifact fill:#f1f5f9,stroke:#64748b,color:#1f2937
  classDef output fill:#dcfce7,stroke:#16a34a,color:#1f2937
  classDef ref fill:#ffffff,stroke:#94a3b8,stroke-dasharray:4 3,color:#64748b
```

Each stage owns one canonical file, and downstream stages annotate it instead of writing a second copy: one product brief, one `shot_rows.json`, and one `model_prompt.md` per variant. Storyboards, previs and identity images are created only when needed; otherwise the manifest records `not_required` with a reason.

## Reference-video recreation

When reference videos are supplied, AdMuse reads them before writing any creative:

- **Download and cuts**: hypit fetches the video, probes duration and framing, proposes candidate cuts and extracts frames; the real edit points are then confirmed by inspection.
- **Speech**: the locally installed Whisper `large-v3-turbo` transcribes the original language with segments, word timings and probabilities. No model is downloaded automatically.
- **Shot blueprint**: every shot records timing, shot size, framing, camera angle, composition, camera movement and speed, focus, light direction, transition, dialogue, ambience and on-screen text, plus what to keep and what to replace.
- **Allocation**: with N references and M requested videos, each reference gets ⌊M/N⌋ videos and the first M mod N references get one more; if M < N, only the first M are used. Ten references and twenty videos means two videos per reference.

## Reference routing

<p align="center"><img src="assets/reference-routing.svg" alt="Four reference-image modes" width="100%"></p>

For each variant the router picks the smallest reference set that still preserves the product look and the action (workflow illustration):

| Mode | Use when |
|---|---|
| `product_images_only` | Source images show the product clearly, it stays in one state, and the action is obvious |
| `identity_plus_product` | Geometry is easy to confuse, several sides are visible, or parts change state |
| `storyboard_plus_product` | Several meaningful shots, or a reveal/proof sequence that text alone will not hold |
| `full_spatial_reference` | Hand contact, installation, axis, light/air/spray direction or complex camera geometry matters |

If a generated identity image changes the SKU, geometry, orientation or control layout, it is discarded and the verified source image is used instead.

## Model backends

| Backend | Duration | Reference images | Prompt | When |
|---|---|---|---|---|
| `minimax-h3` | 4–15 s, 24 FPS | up to 9 | ≤7000 characters | default |
| `omni-flash` / `omni_flash-10s` | ≤10 s | up to 3 | ≤4000 characters | explicitly selected |

If Omni Flash is selected with a 15-second target, AdMuse neither truncates nor switches models silently; it proposes a multi-clip plan or asks you to adjust the brief.

## Physical-causality constraints

For products with directional output, the prompt spells out the causal chain and geometry. For a bike light: the hand presses the button → the button moves down → only the lamp face emits light → the lit patch sits on the ground or wall in front of the lamp axis. Fans, sprays, screens and magnetic accessories get the same source, direction and receiving-surface constraints.

## Delivery and QC

- **Serial submission**: `submission.json` is written before each request and the task ID is recorded immediately; an ambiguous response triggers a status check, never a duplicate submit.
- **Download**: files land as `.part`, are validated, then renamed to `.mp4` with a recorded SHA-256.
- **Two QC passes**: technical QC checks codec, duration, size, frame rate and audio; creative QC samples opening, action, proof and closing frames for SKU, hands, light direction, language and action order.
- **Separate counts**: submitted, remote-final, downloaded, technical pass and creative pass are reported separately. Technical success is not creative acceptance.

## Dependencies

`install.py` searches `~/.agents/skills` and `~/.codex/skills`. Existing skills are always skipped and never overwritten; missing ones are added to `~/.agents/skills` from the sources below.

| Skill | Role | Source |
|---|---|---|
| `ad-muse` | Orchestrator | this repository |
| `commerce-production-workflow` | Production order, gates, cross-artifact QC | this repository (adapted) |
| `commerce-shot-grammar` | Axis, blocking, camera, contact and state | this repository (adapted) |
| `product-ugc-pipeline` | Product scraping, asset manifest, brief, identity references | [peipeijiang/product-ugc-pipeline](https://github.com/peipeijiang/product-ugc-pipeline) |
| `writing-video-prompts` | Model-neutral action and physics draft | [SupercmoHQ/superCMO-skills](https://github.com/SupercmoHQ/superCMO-skills) |
| `minimax-h3-*` (6) | H3 routing, reference/text/keyframe/multishot prompts and review | [unknowlei/minimax-h3-opencode-skills](https://github.com/unknowlei/minimax-h3-opencode-skills) |
| `h3-prompt-writing` | Official H3 prompt syntax | [MiniMax-AI/MiniMax-H3](https://github.com/MiniMax-AI/MiniMax-H3) |
| `hypit` | Reference-video download and analysis | [hypit-ai/hypit](https://github.com/hypit-ai/hypit) |

Local tools are checked, not installed: `git`, `ffmpeg` and `ffprobe` are required; the `hypit` CLI is used for reference-video mode (`npm install -g @hypit/hypit`); Whisper needs a Python that can `import whisper` and cached weights. Add `--verify-asr-hash` to check the official SHA-256 of large-v3-turbo, or `--json` for machine-readable output.

## License

[MIT](LICENSE). Origins of adapted content and licenses of third-party skills are listed in [NOTICE.md](NOTICE.md).
