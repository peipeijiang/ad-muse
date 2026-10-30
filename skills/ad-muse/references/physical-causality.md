# Physical causality rules

Use these as a compact preflight for product videos. They constrain what the prompt says and what the sampled frames must show; they are not a physics simulator.

## Identity and state

- Keep one SKU, variant, silhouette, proportion, material and control layout throughout a variant.
- Define the product state at the start and end of each beat. A state change requires a visible action that causes it.
- A product cannot be open, attached, switched on, filled or worn before the action that causes that state.
- Once a state changes, it remains changed until another visible action reverses it.
- Use source images for any face, back, interior, label or control that the source actually shows. Do not invent hidden geometry.

## Contact and motion

- Each beat has one primary moving action at one object.
- Name the hand that owns the object, the contact point, the grip, the path, the placement and the release.
- Camera motion and object motion must have a common axis and plausible parallax.
- A rigid attachment stays rigid while the camera moves; a handoff needs a visible transfer.
- Count hands. A phone held for a selfie leaves one free hand; a locked camera leaves two.

## Directional effects

For light, airflow, spray, sound emission, magnets, screens or other directional effects, record:

```text
source point → source orientation → direction/axis → receiving surface or object → visible result
```

For a bicycle lamp, the lamp face is the only light source, the beam starts at the lamp face, the axis follows the lamp's forward orientation, and the illuminated patch appears on a surface in front of that axis. The control press precedes illumination. A glow, beam or light patch must not appear from the back, side or empty frame edge.

## QC evidence

Sample at least one frame before the action, one at contact, one at the state change, one at the proof result and the final frame. A prompt that says the right thing without visible evidence remains `needs_review`.
