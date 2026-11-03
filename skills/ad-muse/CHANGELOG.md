# Changelog

## 0.4.0 — 2026-11-03

- Replace product-only preference with per-shot action/evidence routing.
- Add operation/fit references and explicit hand-state coverage; retain storyboard-first spatial planning.
- Require v2 routing validation in request preparation and document the gate for custom submitters.
- Reject incomplete/stale plans and add anatomy-failure escalation and temporal QC.

## 0.3.2 — 2026-11-03

- Align spatial planning with companion workflow v2: storyboard first, then previs referencing storyboard and product identity.
- Keep the spatial map dominant with a product sidebar and compact camera cards; allow targeted framing previews without duplicating the full storyboard.
- Make Hook, location and scale decisions depend on the current storyboard and product dossier.
- Separate conceptual QC, measured geometry verification and user acceptance.
