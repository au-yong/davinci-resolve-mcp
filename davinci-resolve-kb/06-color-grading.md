# 06 — Color Grading & Adjustments

**Where:** Color page (node-based grading). The Edit page Inspector has no color wheels, apart from Resolve FX applied to the clip.

---

## 1. Color Page Palettes

| Palette | Controls | Use |
|---------|----------|-----|
| **Primaries – Color Wheels** | Lift (shadows), Gamma (mids), Gain (highlights), Offset (everything) + Contrast, Pivot, Saturation, Hue, Temp, Tint, Midtone Detail, Color Boost, Shadows, Highlights | Balance and exposure, the first step |
| **Primaries – Log Wheels** | Shadow / Midtone / Highlight, with range controls | Film-style control on log footage |
| **HDR Palette** | Zone-based wheels (Black, Dark, Shadow, Light, Highlight, Specular) | Precise tonal zones; works on SDR too |
| **Curves** | Custom (YRGB), Hue vs Hue, Hue vs Sat, Hue vs Lum, Lum vs Sat, Sat vs Sat, Sat vs Lum | Contrast S-curve, targeted hue fixes |
| **Color Warper** | Hue-Saturation mesh and Chroma-Luma grids | Intuitive hue shifting (e.g. teal-orange) |
| **Qualifier** | HSL / RGB / Luma / 3D keys | Isolate skin, sky, a specific color |
| **Power Windows** | Linear, Circle, Polygon, Curve, Gradient shapes | Localize corrections (vignette, face light) |
| **Tracker** | Point/cloud tracking, stabilizer | Make windows follow the subject |
| **Magic Mask** ⭐ | AI person/object/feature isolation | Isolate people without roto |
| **Blur / Sharpen / Mist** | Spatial filters | Soften backgrounds, sharpen eyes |
| **Key** | Key input/output gain, matte finesse | Refine qualifier mattes |
| **Sizing** | Input/Output/Node sizing | Reframe, stabilization offset |
| **Motion Effects** ⭐ | Temporal/Spatial Noise Reduction, Motion Blur | Denoise |
| **Scopes** | Waveform, Parade, Vectorscope, Histogram, CIE | Objective measurement |
| **Gallery** | Stills, PowerGrades | Reference, reuse looks |

## 2. Professional Node Order (serial nodes)

| # | Node | Purpose |
|---|------|---------|
| 1 | **Input / CST** | Convert camera log → working/display space (Color Space Transform, or project Color Management) |
| 2 | **Noise Reduction** ⭐ | Denoise early (before contrast) |
| 3 | **Exposure / Balance** | Offset for exposure; Gain/Lift for white/black balance |
| 4 | **Contrast** | Contrast + Pivot, or a curve |
| 5 | **Saturation** | Overall saturation / Color Boost |
| 6 | **Secondary – Skin** | Qualifier on skin; keep near the vectorscope skin-tone line |
| 7 | **Secondary – Sky/BG** | Qualifier or window |
| 8 | **Windows / Relight** | Vignette, face light, background darkening |
| 9 | **Look** | Creative LUT at 30–70% key output, or a manual teal/orange split |
| 10 | **Texture** | Halation ⭐ / Glow / Film Grain ⭐ |
| 11 | **Output / Legalize** | Gamut limiter, final CST if needed |

## 3. Technical Targets (Rec.709 SDR)

| Measure | Target |
|---------|--------|
| Blacks | Waveform about 0–5% (not crushed unless stylistic) |
| Whites | About 90–100%, not clipped (unless specular highlights) |
| Skin tones | On or near the vectorscope **skin-tone line** (≈ 11 o'clock) |
| Skin luminance | About 50–70% on the waveform for well-lit faces |
| Neutral grays | Parade R=G=B |
| Saturation | No colors past the vectorscope target boxes for broadcast |

---

## 4. Scripting the Grade

> **No API creates nodes**, adds windows/qualifiers, or moves wheels. Script with **CDL, LUT, DRX, versions, groups, and copy-grade**.

### CDL (primary correction in one call)
```python
item.SetCDL({
    "NodeIndex": "1",
    "Slope":  "1.05 1.00 0.95",   # per-channel gain-like multiplier (R G B); >1 brighter/warmer if R up
    "Offset": "0.00 0.00 0.01",   # per-channel lift/offset add
    "Power":  "1.00 1.00 1.00",   # per-channel gamma (<1 brighter mids, >1 darker mids)
    "Saturation": "1.10",
})
```
| Want | CDL change |
|------|-----------|
| Brighter overall | Slope up evenly (1.05–1.15) |
| Warmer | Slope R up / B down slightly (e.g. `1.04 1.00 0.96`) |
| Cooler | Slope B up / R down |
| Lifted, faded blacks | Offset +0.02–0.04 all channels |
| More contrast in mids | Power up slightly (1.05–1.1) + Slope up |
| Desaturate | Saturation 0.7–0.9 |
| B&W | Saturation 0 |

### LUTs
```python
project.RefreshLUTList()                       # after adding new .cube files to the LUT folder
graph = item.GetNodeGraph()                    # optional layer index argument
graph.SetLUT(1, "Blackmagic Design/Blackmagic Design Film to Video.cube")   # relative to the LUT folder, or absolute
graph.GetLUT(1)
```
LUT folder (macOS): `/Library/Application Support/Blackmagic Design/DaVinci Resolve/LUT/`

### DRX looks (includes Resolve FX, windows, qualifiers)
```python
graph.ApplyGradeFromDRX("/Looks/teal_orange.drx", 0)   # 0 = no keyframes, 1 = source TC aligned, 2 = start frames aligned
```

### Node control & inspection
```python
n = graph.GetNumNodes()
for i in range(1, n + 1):
    print(i, graph.GetNodeLabel(i), graph.GetToolsInNode(i))
graph.SetNodeEnabled(3, False)      # bypass node 3 (e.g. turn off the grain)
graph.ResetAllGrades()
```

### Versions (non-destructive A/B)
```python
item.AddVersion("Warm look", 0)     # 0 = local, 1 = remote
item.LoadVersionByName("Warm look", 0)
item.GetVersionNameList(0)
```

### Apply to many clips
```python
src.CopyGrades([clip2, clip3, clip4])           # copies the current node-stack layer grade

group = project.AddColorGroup("Interview A-cam")
for c in clips: c.AssignToColorGroup(group)
post = group.GetPostClipNodeGraph()             # a shared look for the whole group
post.ApplyGradeFromDRX("/Looks/film_look.drx", 0)

timeline.GetNodeGraph().SetLUT(1, "...")        # timeline-level node graph affects every clip
```

### AI / analysis tools
```python
item.CreateMagicMask("BI")    # Studio; tracks a mask bidirectionally (needs a mask stroke set up in the UI)
item.Stabilize()
item.SmartReframe()           # Studio; reframes for a different timeline aspect ratio
item.ExportLUT(resolve.EXPORT_LUT_33PTCUBE, "/out/clip_look.cube")
timeline.GrabStill(); timeline.GrabAllStills(2)    # 2 = middle frame
project.ExportCurrentFrameAsStill("/out/frame.png")
```

---

## 5. Look Recipes (manual values, for guiding the user or building DRX files)

| Look | Steps |
|------|-------|
| **Teal & Orange** | Balance → Color Warper: push shadows/blues toward teal, keep skin orange → Sat 1.1 → protect skin with a qualifier |
| **Bleach Bypass** | Saturation 0.4–0.6 → strong contrast S-curve → slight cool tint |
| **Warm Golden Hour** | Gain toward orange (+temp), Lift slightly toward blue for contrast → Glow low |
| **Moody Dark** | Lower Gamma, crush blacks slightly, desaturate greens (Hue vs Sat), vignette |
| **Clean Corporate** | Neutral balance, gentle contrast, Sat 1.05, sharpen 0.1, no stylization |
| **Day-for-Night** | Underexpose 1.5–2 stops, Sat 0.5, Lift/Gamma toward blue, darken sky with a window |
| **Vintage Film** | Offset blacks up (fade), Lift toward green/teal, Gain warm, Halation ⭐ + Film Grain ⭐ |
| **Black & White** | Saturation 0 → use RGB Mixer (monochrome) to control channel contribution → contrast curve |

## 6. Color Management (project setting)
```python
project.SetSetting("colorScienceMode", "davinciYRGBColorManagedv2")   # Resolve Color Management
project.GetSetting()                                                     # dump every key and its current value
```
> Setting key names differ by version. Always dump `project.GetSetting()` first and use the exact keys and values it shows.

## 7. UI Click Paths

- **Add a serial node:** Color page → Node editor → `Option/Alt+S`. Parallel: `Option/Alt+P`. Layer: `Option/Alt+L`.
- **Save a look:** right-click the viewer → **Grab Still** → Gallery → right-click → **Export** (`.drx`), or drag into a PowerGrade album.
- **Apply a LUT:** right-click a node → LUT → choose.
- **Shot match:** select the target clip → right-click the reference thumbnail → **Shot Match to This Clip**.
