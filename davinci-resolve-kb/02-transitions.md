# 02 — Transitions

**Where:** Edit page → Effects → **Toolbox → Video Transitions / Audio Transitions**, plus **Fusion Transitions** and **OpenFX → Transitions**.

> [!IMPORTANT]
> **Automation:** No API adds transitions. Options, best first:
> 1. **Guide the user** (fast and reliable): select the edit points → `Cmd/Ctrl+T` adds the *standard transition* (Cross Dissolve by default) to all selected edits.
> 2. **FCPXML round-trip** (W4 in [00](00-capability-matrix.md)) for dissolves.
> 3. **Fusion fade** for fade-in/out on a single clip ([04](04-fusion-scripting.md), recipe "Fade in/out").

---

## Handles Requirement
A transition needs **handles**: unused source frames beyond the clip's in/out points. A 1-second centered transition needs about 12–15 frames of handle on each side. If a transition won't apply or comes out shorter, the clips lack handles.
- API check: `item.GetLeftOffset()` / `item.GetRightOffset()` return the available extension in frames.

## Video Transitions

| Group | Transitions | When to use |
|-------|-------------|-------------|
| **Dissolve** | Cross Dissolve, Additive Dissolve, Non-Additive Dissolve, Blur Dissolve, Dip to Color Dissolve, **Smooth Cut** | Cross Dissolve = passage of time, soft scene change. Dip to Black = chapter/section end. **Smooth Cut** hides jump cuts in interviews (use 2–6 frames only) |
| **Iris** | Arrow, Cross, Diamond, Eye, Hexagon, Oval, Pentagon, Square, Triangle Iris | Retro, playful, kids content |
| **Motion** | Barn Door, Push, Slide, Split, Band Slide | Energetic, social media, slideshows |
| **Shape** | Box, Heart, Star, Triangle | Novelty |
| **Wipe** | Band, Center, Clock, Edge, Radial, Spiral, Venetian Blind, X Wipe | Classic broadcast, retro reveals |
| **Fusion Transitions** | Template transitions (flash, zoom, blur-push, slide variants; exact names vary by version) | Modern YouTube-style whooshes |
| **Resolve FX Transitions** | GPU transitions (e.g. glitch, warp, blur, burn-style) | Stylized accents |

### Transition Inspector parameters
| Parameter | Meaning |
|-----------|---------|
| **Duration** | Frames or seconds (typical: 12–24 frames for dissolves at 24/25 fps) |
| **Alignment** | Center on Edit / Start on Edit / End on Edit |
| **Transition Curve / Ease** | Linear, Ease In, Ease Out, Ease In & Out |
| **Color** | For Dip to Color (black/white) |
| **Border / Feather** | For wipes and iris shapes |
| **Angle / Direction** | For push, slide, wipe |

## Audio Transitions

| Transition | Use it for |
|------------|-----------|
| **Cross Fade 0 dB** | Linear fade; good when the two signals are correlated (same mic/room) |
| **Cross Fade +3 dB** | Equal-power fade; best default for music or uncorrelated sounds (avoids the mid-fade dip) |
| **Cross Fade −3 dB** | Special cases with correlated signals |

**Quick fades without a transition:** hover the top corner of an audio clip on the timeline and drag the white fade handle. A 2–10 frame fade at every audio cut removes clicks and pops.

## Editorial Guidelines

| Situation | Recommendation |
|-----------|----------------|
| Interview jump cut | Hard cut + B-roll cover, or Smooth Cut 2–6 frames |
| Time passing | Cross Dissolve 1–2 s |
| End of video / section | Dip to Black 0.5–1 s, with an audio fade out |
| Fast montage | Mostly hard cuts on the beat; occasional Push/Zoom Fusion transitions |
| Corporate | Cross Dissolve or hard cuts only; avoid shapes and iris |
| Music change | Audio Cross Fade +3 dB over 1–3 s |

**Rule:** the default is a **hard cut**. Use transitions on purpose, not on every edit.

---

## UI Click Paths

- **Add the standard transition to many edits:** select clips (or edit points with `U` trim mode) → **Timeline → Add Transition** (`Cmd/Ctrl+T`).
- **Change the standard transition:** Effects → right-click a transition → **Set as Standard Transition**.
- **Audio-only crossfade:** select audio edit points → `Shift+T` (*Add Audio Only Transition*; verify the shortcut in Keyboard Customization).
- **Change duration:** select the transition → Inspector → Duration, or drag its edge on the timeline.

## FCPXML Round-Trip (advanced automation)

1. In the UI, add **one** Cross Dissolve to a test timeline and export it: `timeline.Export("/tmp/ref.fcpxml", resolve.EXPORT_FCPXML_1_10, resolve.EXPORT_NONE)`.
2. Inspect the `<transition>` element Resolve wrote, and use it as your template (timing attributes are rational seconds, e.g. `"12/24s"`).
3. Export the real timeline, insert transition elements at the cuts between spine clips, and save.
4. `mediaPool.ImportTimelineFromFile("/tmp/edited.fcpxml", {"timelineName": "Edit v2 (transitions)"})`.
5. Verify visually; Fusion and Resolve FX attributes may not survive the round-trip.
