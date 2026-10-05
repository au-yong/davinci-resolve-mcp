# 04 — Fusion Scripting: Graphics & Effects in Code

Fusion is the agent's **most powerful scripting surface** for visual effects and motion graphics. Every timeline clip can own one or more Fusion compositions, and inside a comp the agent can add tools, wire nodes, set values, and keyframe them.

---

## 1. Getting a Comp

```python
item = timeline.GetItemListInTrack("video", 1)[0]   # or timeline.GetCurrentVideoItem()

comp = item.GetFusionCompByIndex(1) if item.GetFusionCompCount() > 0 else item.AddFusionComp()
# Other options:
# comp = item.ImportFusionComp("/path/template.comp")   # adds a new comp from a file
# item.LoadFusionCompByName("Composition 2")             # switch the active comp
# item.ExportFusionComp("/path/out.comp", 1)              # save comp 1 as a template
```

A fresh clip comp contains **`MediaIn1`** (the clip's image) → **`MediaOut1`** (what the timeline shows). Effects go **between** them.

### Comp time
Keyframe times are **comp frames**. Read the comp's range before keyframing:
```python
attrs = comp.GetAttrs()
start, end = attrs["COMPN_RenderStart"], attrs["COMPN_RenderEnd"]
```

### Batch safety
```python
comp.Lock()                       # stop re-rendering/dialogs while editing
comp.StartUndo("Agent: add glow")
# ... edits ...
comp.EndUndo(True)
comp.Unlock()
```

---

## 2. Core API (Fusion objects)

| Call | Purpose |
|------|---------|
| `comp.AddTool(toolID, x=-32768, y=-32768)` | Add a tool (the default coords auto-place it). Returns the tool |
| `comp.FindTool("Blur1")` | Find by node name |
| `comp.FindToolByID("TextPlus")` | Find the first tool of a type |
| `comp.GetToolList(selectedOnly=False, toolID=None)` | `{index: tool}` dict |
| `tool.SetInput(name, value, time=None)` | Set a value (at `time` if animated) |
| `tool.GetInput(name, time=None)` | Read a value |
| `tool.ConnectInput(inputName, otherTool)` | Wire `otherTool`'s main output into `inputName` (`None` disconnects) |
| `tool.AddModifier(inputName, "BezierSpline")` | Make an input animatable (keyframes) |
| `tool.GetInputList()` | Discover the real input names/IDs |
| `tool.SetAttrs({"TOOLS_Name": "MyGlow"})` | Rename a node |
| `tool.SetAttrs({"TOOLB_PassThrough": True})` | Bypass a node (toggle the effect off) |
| `tool.Delete()` | Remove a node |

**Value formats:** numbers are floats; **points** are `{1: x, 2: y}` in 0–1 normalized space (0,0 = bottom-left, 0.5,0.5 = center); colors are separate `Red/Green/Blue/Alpha` inputs in 0–1; combo boxes take an int index or a string, depending on the tool.

---

## 3. Tool ID Catalog (most useful for agents)

> IDs are the internal registry names used by `AddTool`. Confirm unknown ones by adding the tool in the UI and reading `tool.ID`, or by listing `fusion.GetRegList()`.

### I/O & Compositing
| ID | Tool | Key inputs |
|----|------|------------|
| `MediaIn` / `MediaOut` | Clip input / output | (exists in clip comps) |
| `Loader` | Load an image/sequence from disk (logos, PNG overlays) | `Clip` (file path) |
| `Merge` | Layer foreground over background | `Background`, `Foreground`, `Blend` (0–1), `ApplyMode`, `Center`, `Size`, `Angle` |
| `Dissolve` | Mix two inputs | `Background`, `Foreground`, `Mix` |
| `ChannelBoolean` | Channel math | `Operation` |
| `MatteControl` | Combine/adjust alpha | `Garbage Matte`, `Solid Matte` |

### Generators & Text
| ID | Tool | Key inputs |
|----|------|------------|
| `TextPlus` | Text+ (2D text) | `StyledText`, `Font`, `Style`, `Size`, `Center`, `Red1`/`Green1`/`Blue1`/`Alpha1` |
| `Text3D` | Extruded 3D text | `StyledText`, `Font`, `ExtrusionDepth` |
| `Background` | Solid/gradient color | `TopLeftRed`, `TopLeftGreen`, `TopLeftBlue`, `TopLeftAlpha`, `Type` |
| `FastNoise` | Procedural noise (fog, texture, shimmer) | `Detail`, `Contrast`, `Brightness`, `XScale`, `SeetheRate` |
| `sRectangle`, `sEllipse`, `sStar`, `sRender`, `sMerge` | Shape system (vector shapes for motion design) | `Width`, `Height`, `CornerRadius` |
| `pEmitter` → `pRender` | Particles | `Number`, `Lifespan`, `Velocity` |

### Transform & Motion
| ID | Tool | Key inputs |
|----|------|------------|
| `Transform` | Move/scale/rotate | `Center`, `Size`, `Angle`, `Pivot`, `FlipHoriz`, `FlipVert` |
| `DVE` | 3D-perspective transform | `XRotation`, `YRotation`, `ZRotation`, `Center` |
| `Crop` | Crop | `XOffset`, `YOffset`, `XSize`, `YSize` |
| `Resize` / `Scale` | Change resolution | `Width`, `Height` / `XSize` |
| `Letterbox` | Fit to an aspect | `Width`, `Height` |
| `CameraShake` | Procedural shake | deviation/speed inputs (verify names with `GetInputList()`) |
| `Tracker` | Point tracking | track points |
| `PlanarTracker` | Planar tracking (screens, signs) | |
| `CornerPositioner` | Corner-pin an image onto a surface | `TopLeft`, `TopRight`, `BottomLeft`, `BottomRight` |

### Blur, Glow, Texture
| ID | Tool | Key inputs |
|----|------|------------|
| `Blur` | Gaussian/box blur | `XBlurSize` (0–100+), `Filter`, `LockXY` |
| `DirectionalBlur` | Linear/radial/zoom/centered blur | `Type`, `Length`, `Angle`, `Center` |
| `Defocus` | Lens-style defocus | `XDefocusSize`, `BloomLevel` |
| `Glow` | Glow on highlights | `XGlowSize`, `Glow` (strength) |
| `SoftGlow` | Diffuse glow | `Threshold`, `Gain` |
| `UnsharpMask` / `Sharpen` | Sharpening | `XSize`, `Amount` |
| `FilmGrain` | Film grain | size/strength inputs (verify) |
| `Highlight` | Star highlights | |
| `Rays` | Volumetric rays | `Center`, `Decay` |

### Color
| ID | Tool | Key inputs |
|----|------|------------|
| `BrightnessContrast` | Quick exposure | `Gain`, `Lift`, `Gamma`, `Contrast`, `Brightness`, `Saturation` |
| `ColorCorrector` | Wheels/levels | `MasterRGBGain`, `MasterSaturation`, … |
| `ColorCurves` | Curves | |
| `HueCurves` | Hue vs. X | |
| `ColorSpaceTransform` / `Gamut` | Color space conversion | |

### Masks (connect to a tool's `EffectMask`, or Merge's mask)
| ID | Mask | Key inputs |
|----|------|------------|
| `EllipseMask` | Oval | `Center`, `Width`, `Height`, `SoftEdge`, `Invert` |
| `RectangleMask` | Rectangle | `Center`, `Width`, `Height`, `CornerRadius`, `SoftEdge` |
| `PolylineMask` / `BSplineMask` | Freeform | points |
| `MagicMask`-style AI isolation | Use the Color page instead (`item.CreateMagicMask`) | |

### Keying
| ID | Tool |
|----|------|
| `DeltaKeyer` | High-quality green/blue screen keyer |
| `UltraKeyer` | Alternative keyer |
| `LumaKeyer`, `ChromaKeyer` | Simple keys |

---

## 4. Helper: Insert an Effect Between MediaIn and MediaOut

```python
def insert_effect(comp, tool_id, settings=None, name=None):
    """Insert tool_id just before MediaOut1 and return the tool."""
    media_out = comp.FindTool("MediaOut1")
    upstream = media_out.Input.GetConnectedOutput().GetTool()   # whatever feeds MediaOut now
    tool = comp.AddTool(tool_id, -32768, -32768)
    if name:
        tool.SetAttrs({"TOOLS_Name": name})
    tool.ConnectInput("Input", upstream)
    media_out.ConnectInput("Input", tool)
    for k, v in (settings or {}).items():
        tool.SetInput(k, v)
    return tool
```
> `Merge`-type tools use `Background`/`Foreground` instead of `Input`. For those, wire manually as in the recipes below.

---

## 5. Recipes

### R1 — Blur the whole clip
```python
insert_effect(comp, "Blur", {"XBlurSize": 8.0}, name="AgentBlur")
```

### R2 — Background blur with a sharp center (spotlight/focus)
```python
blur = insert_effect(comp, "Blur", {"XBlurSize": 15.0})
mask = comp.AddTool("EllipseMask")
mask.SetInput("Center", {1: 0.5, 2: 0.5})
mask.SetInput("Width", 0.45); mask.SetInput("Height", 0.6)
mask.SetInput("SoftEdge", 0.15)
mask.SetInput("Invert", 1)                # blur everything OUTSIDE the ellipse
blur.ConnectInput("EffectMask", mask)
```

### R3 — Vignette
```python
bc = insert_effect(comp, "BrightnessContrast", {"Gain": 0.6})
m = comp.AddTool("EllipseMask")
m.SetInput("Width", 0.9); m.SetInput("Height", 0.9); m.SetInput("SoftEdge", 0.35); m.SetInput("Invert", 1)
bc.ConnectInput("EffectMask", m)
```

### R4 — Logo watermark, bottom-right, 80% opacity
```python
media_in, media_out = comp.FindTool("MediaIn1"), comp.FindTool("MediaOut1")
logo = comp.AddTool("Loader"); logo.SetInput("Clip", "/Users/me/brand/logo.png")
merge = comp.AddTool("Merge")
merge.ConnectInput("Background", media_in)
merge.ConnectInput("Foreground", logo)
merge.SetInput("Center", {1: 0.9, 2: 0.1})
merge.SetInput("Size", 0.15)
merge.SetInput("Blend", 0.8)
media_out.ConnectInput("Input", merge)
```
> If `Loader` paths fail in your version, import the logo into the Media Pool and use a second `MediaIn`, or put the logo on V2 and use `SetProperty` (Zoom/Pan/Opacity) instead.

### R5 — Fade in and out (opacity via Merge over black)
```python
media_in, media_out = comp.FindTool("MediaIn1"), comp.FindTool("MediaOut1")
bg = comp.AddTool("Background")                       # black by default
for c in ("TopLeftRed", "TopLeftGreen", "TopLeftBlue"): bg.SetInput(c, 0.0)
bg.SetInput("TopLeftAlpha", 1.0)
merge = comp.AddTool("Merge")
merge.ConnectInput("Background", bg)
merge.ConnectInput("Foreground", media_in)
media_out.ConnectInput("Input", merge)

a = comp.GetAttrs(); s, e = a["COMPN_RenderStart"], a["COMPN_RenderEnd"]
fps_fade = 12                                          # frames
merge.AddModifier("Blend", "BezierSpline")
merge.SetInput("Blend", 0.0, s)
merge.SetInput("Blend", 1.0, s + fps_fade)
merge.SetInput("Blend", 1.0, e - fps_fade)
merge.SetInput("Blend", 0.0, e)
```

### R6 — Punch-in zoom (emphasis) at a moment
```python
tr = insert_effect(comp, "Transform")
tr.AddModifier("Size", "BezierSpline")
hit = s + 48                                           # frame of the emphasis
tr.SetInput("Size", 1.0, hit - 1)
tr.SetInput("Size", 1.15, hit)                         # hard 15% punch-in
tr.SetInput("Size", 1.15, hit + 36)
tr.SetInput("Size", 1.0, hit + 37)
```
For a smooth Ken Burns effect instead, key `Size` 1.0 → 1.1 across the whole clip, plus `Center` drift.

### R7 — Animated lower third (bar + name, slides in from left)
```python
media_in, media_out = comp.FindTool("MediaIn1"), comp.FindTool("MediaOut1")

bar = comp.AddTool("Background")
bar.SetInput("TopLeftRed", 0.05); bar.SetInput("TopLeftGreen", 0.35); bar.SetInput("TopLeftBlue", 0.85); bar.SetInput("TopLeftAlpha", 0.9)
bar_mask = comp.AddTool("RectangleMask")
bar_mask.SetInput("Center", {1: 0.25, 2: 0.17}); bar_mask.SetInput("Width", 0.38); bar_mask.SetInput("Height", 0.09)
bar_mask.SetInput("CornerRadius", 0.1)
bar.ConnectInput("EffectMask", bar_mask)

txt = comp.AddTool("TextPlus")
txt.SetInput("StyledText", "Jane Doe\nProduct Designer")
txt.SetInput("Size", 0.045); txt.SetInput("Center", {1: 0.25, 2: 0.17})
txt.SetInput("HorizontalJustificationNew", 0)

m1 = comp.AddTool("Merge"); m1.ConnectInput("Background", media_in); m1.ConnectInput("Foreground", bar)
m2 = comp.AddTool("Merge"); m2.ConnectInput("Background", m1);       m2.ConnectInput("Foreground", txt)
media_out.ConnectInput("Input", m2)

# slide in: animate both merges' Center x from off-screen to place
for m in (m1, m2):
    m.AddModifier("Center", "BezierSpline")
    m.SetInput("Center", {1: -0.5, 2: 0.5}, s + 10)
    m.SetInput("Center", {1: 0.5,  2: 0.5}, s + 25)
    m.SetInput("Center", {1: 0.5,  2: 0.5}, s + 25 + 120)   # hold ~5 s at 24 fps
    m.SetInput("Center", {1: -0.5, 2: 0.5}, s + 25 + 135)
```

### R8 — Color tint / stylized look
```python
insert_effect(comp, "BrightnessContrast", {"Saturation": 0.7, "Contrast": 0.1, "Gamma": 0.95})
```

### R9 — Glow on highlights
```python
insert_effect(comp, "SoftGlow", {"Threshold": 0.75, "Gain": 0.6})
```

### R10 — Picture-in-picture
Simpler on the Edit page: put clip B on V2 and use `SetProperty` (see [07](07-inspector-properties.md)):
```python
b.SetProperty({"ZoomX": 0.35, "ZoomY": 0.35, "Pan": 600, "Tilt": 300})
```

---

## 6. Fusion Templates Workflow (recommended for brands)

1. A human designs the graphic in the Fusion page, with clearly named nodes (`TitleText`, `BrandBar`).
2. Export it: `item.ExportFusionComp("/brand/lower_third.comp", 1)`.
3. The agent reuses it on any clip:
   ```python
   comp = clip.ImportFusionComp("/brand/lower_third.comp")
   comp.FindTool("TitleText").SetInput("StyledText", "New Name")
   ```
Named nodes make agent edits deterministic. Document each template's editable node and input names next to the file (e.g. `lower_third.json`).

## 7. Pitfalls

- **Comp not on screen:** edits happen even when the Fusion page isn't open. `fusion.GetCurrentComp()` only works on the Fusion page; prefer `item.GetFusionCompByIndex()`.
- **Performance:** heavy comps slow playback; call `item.SetFusionOutputCache(...)` to render-cache.
- **Resolution:** Fusion works in the timeline resolution; `Size`/`Center` are normalized, so values carry across resolutions.
- **Keyframes overwrite:** `SetInput(name, v, t)` on an animated input sets or replaces the key at `t`.
- **Python vs. Lua:** examples are Python. In Lua, use `tool:SetInput(...)` with colon syntax.
