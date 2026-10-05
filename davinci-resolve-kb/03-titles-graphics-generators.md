# 03 — Titles, Graphics, Generators & Subtitles

**Where:** Edit page → Effects → **Toolbox → Titles / Generators**, **Fusion Titles**, **Fusion Generators**, **OpenFX → Generators**. Also the Effects Library on the Cut page.

---

## 1. API Functions for Inserting Graphics

All of these are `Timeline` methods. They insert **at the playhead**, on the track chosen by Resolve's destination/auto-track logic, using the **Standard Generator Duration** from User Preferences → Editing (default about 5 s). They return a `TimelineItem`, or `None` if the name doesn't match.

| Method | Example name argument |
|--------|-----------------------|
| `InsertTitleIntoTimeline(name)` | `"Text"`, `"Scroll"`, `"Left Lower Third"`, `"Middle Lower Third"`, `"Right Lower Third"` |
| `InsertFusionTitleIntoTimeline(name)` | `"Text+"`, or any Fusion Title template name exactly as shown in the Effects Library |
| `InsertGeneratorIntoTimeline(name)` | `"Solid Color"`, `"Window"`, `"Four Color Gradient"`, `"Grey Scale"`, `"SMPTE Color Bar"`, `"EBU Color Bar"`, `"10 Step"`, `"100mV Steps"`, `"YCbCr Ramp"` |
| `InsertFusionGeneratorIntoTimeline(name)` | `"Contours"`, `"Noise Gradient"`, `"Paper"`, `"Texture Background"` (names vary by version) |
| `InsertOFXGeneratorIntoTimeline(name)` | OFX generator names from OpenFX → Generators |
| `InsertFusionCompositionIntoTimeline()` | (no args) empty Fusion comp clip for fully custom graphics |

> [!NOTE]
> There's **no API to set a timeline item's duration or move it**. Control length with the Standard Generator Duration preference (UI), or build the graphic inside a Fusion comp attached to an existing clip of the right length.

### Insert a title at a timecode and set its text
```python
timeline = project.GetCurrentTimeline()
timeline.SetCurrentTimecode("01:00:10:00")          # move playhead first
item = timeline.InsertFusionTitleIntoTimeline("Text+")
if item is None:
    raise RuntimeError("Title name not found")

comp = item.GetFusionCompByIndex(1)
text = comp.FindToolByID("TextPlus") or comp.FindTool("Template")
comp.Lock()                                         # batch edits without re-rendering
text.SetInput("StyledText", "Chapter 1 — The Beginning")
text.SetInput("Font", "Open Sans")
text.SetInput("Style", "Bold")
text.SetInput("Size", 0.08)
text.SetInput("Center", {1: 0.5, 2: 0.15})          # x, y in 0–1 (0,0 = bottom-left)
text.SetInput("Red1", 1.0); text.SetInput("Green1", 1.0); text.SetInput("Blue1", 1.0)
comp.Unlock()
print(item.GetTrackTypeAndIndex(), item.GetStart(), item.GetDuration())
```
> If `FindToolByID` returns `None`, list tools with `comp.GetToolList(False)` and look for the one whose `.ID == "TextPlus"`. Template titles often name the tool `Template`, or wrap it in a macro/group.

---

## 2. Title Types

| Type | Engine | Strengths | Edit text via API? |
|------|--------|-----------|---------------------|
| **Text** (basic title) | Edit page | Simple, fast | Limited; properties are not exposed in Fusion |
| **Text+** | Fusion | Full typography, shading layers, outlines, shadows, per-character animation, keyframes | ✅ via the Fusion comp |
| **Fusion Title templates** | Fusion macros | Pre-animated lower thirds, call-outs, reveals | ✅ via the Fusion comp (input names vary per template) |
| **Scroll** | Edit page | Credits roll | Limited |
| **Subtitles** | Subtitle track | Captions, SRT export | Create via `CreateSubtitlesFromAudio`; editing text is UI-only |

**Recommendation for agents:** use **Text+** or your own **Fusion template** (`ImportFusionComp`) for anything the agent must edit later.

### Text+ key inputs (Fusion `TextPlus` tool)
| Input | Type | Notes |
|-------|------|-------|
| `StyledText` | string | The text. Use `\n` for line breaks |
| `Font`, `Style` | string | Font family and style (`"Bold"`, `"Regular"`) |
| `Size` | float | Relative to frame width, about 0.05–0.12 for titles |
| `Center` | point `{1:x, 2:y}` | 0–1 normalized; `{1:0.5, 2:0.5}` = center |
| `CharacterSpacing`, `LineSpacing` | float | Tracking and leading (1.0 = default) |
| `HorizontalJustificationNew`, `VerticalJustificationNew` | int | 0 = left/top, 1 = center, 2 = right/bottom (verify) |
| `Red1`/`Green1`/`Blue1`/`Alpha1` | float 0–1 | Shading element 1 (fill) color |
| Elements 2–8 (`Red2`…, `Enabled2`…) | | Outline, border, shadow layers |

> Input names can differ across versions. Always confirm with `text.GetInputList()` (returns `{index: Input}`; each `Input` has `.Name` and `.ID`).

---

## 3. Generators

| Generator | Use |
|-----------|-----|
| **Solid Color** | Backgrounds, color mattes for blend modes, black slugs |
| **Window** | Shape mattes |
| **Four Color Gradient** | Animated or static gradient backgrounds |
| **SMPTE / EBU Color Bars, Grey Scale, 10 Step, YCbCr Ramp** | Technical test signals, calibration, broadcast leaders |
| **Fusion generators** (Contours, Noise Gradient, Paper, Texture Background…) | Motion backgrounds for titles |
| **Adjustment Clip** (Effects → Toolbox → Effects) | Apply an effect/grade to all clips beneath it. **Not insertable via API**; place it manually |

---

## 4. Subtitles & Captions

### Auto-generate (Studio)
```python
ok = timeline.CreateSubtitlesFromAudio({
    resolve.SUBTITLE_LANGUAGE: resolve.AUTO_CAPTION_ENGLISH,
    resolve.SUBTITLE_CAPTION_PRESET: resolve.AUTO_CAPTION_SUBTITLE_DEFAULT,  # or AUTO_CAPTION_NETFLIX / AUTO_CAPTION_TELETEXT
    resolve.SUBTITLE_CHARS_PER_LINE: 32,     # 1–60 (default 42)
    resolve.SUBTITLE_LINE_BREAK: resolve.AUTO_CAPTION_LINE_DOUBLE,
    resolve.SUBTITLE_GAP: 0,                 # 0–10 frames
})
```
Languages: Auto, Danish, Dutch, English, French, German, Italian, Japanese, Korean, Mandarin Simplified/Traditional, Norwegian, Portuguese, Russian, Spanish, Swedish.

### Deliver subtitles
```python
project.SetRenderSettings({"ExportSubtitle": True, "SubtitleFormat": "BurnIn"})  # or "EmbeddedCaptions", "SeparateFile"
```

### Subtitle guidelines
| Rule | Value |
|------|-------|
| Max characters per line | 42 (broadcast/Netflix-style); 16 for CJK; 20–32 for vertical social video |
| Max lines | 2 |
| Duration per subtitle | about 1–7 s |
| Reading speed | about 17 characters per second for adults |
| Gap between subtitles | ≥ 2 frames |
| Social media "karaoke" captions | 1–3 words per caption, large bold font, center-lower area |

Styling (font, size, background box, outline) is **UI-only**: select the subtitle track header → Inspector → **Track** tab → Style.

---

## 5. Graphic Design Guidelines for the Agent

| Topic | Guideline |
|-------|-----------|
| **Title-safe area** | Keep text within the inner 90% (action safe 93–95%). Toggle via View → Safe Area |
| **Lower third position** | Bottom-left, about 10% from the left edge and 15–20% from the bottom |
| **On-screen duration** | ≥ the time to read the text twice; lower thirds 4–6 s |
| **Fonts** | Max 2 font families per video; sans-serif for screens |
| **Contrast** | White text with a subtle shadow/outline or a semi-transparent box (`Alpha` 0.5–0.7) on busy footage |
| **Animation timing** | In 10–20 frames, hold, out 8–15 frames; ease in/out rather than linear |
| **Vertical 9:16** | Keep text out of the top 15% and bottom 25% (platform UI overlays) |
| **Brand consistency** | Save styled titles as Fusion templates or Edit-page **Effects → Favorites** |

## 6. UI Click Paths

- **Add a title:** Edit page → Effects → Titles → drag onto a track above the video → Inspector → **Video** (text settings) / **Settings**.
- **Edit Text+ in Fusion:** select the title → click the Fusion page → Inspector shows full Text+ controls; keyframe with the diamond button.
- **Save a custom title as a template:** Fusion page → select nodes → right-click → **Macro → Create Macro** → save into the `Templates/Edit/Titles` folder.
- **Credits roll:** Titles → **Scroll** → paste the text → set duration.
