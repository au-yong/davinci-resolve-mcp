# 07 — Inspector Properties (`TimelineItem.SetProperty`)

The exact keys accepted by `TimelineItem.SetProperty(key, value)` / `GetProperty(key)`, from the Resolve v21.0.4 scripting reference. These map to the Edit page Inspector → **Video** tab (Transform, Cropping, Dynamic Zoom, Composite, Speed/Retime, Scaling, Lens Correction).

```python
item.SetProperty("ZoomX", 1.2)                       # single key
item.SetProperty({"ZoomX": 1.2, "ZoomY": 1.2})       # or a dict of several keys
item.GetProperty()                                   # dict of ALL supported keys and current values
```
- Out-of-range values are **clipped**.
- "width"/"height" mean the timeline resolution (UI max limits).
- Getting an enum key returns its **integer** value.
- Properties are **static**: no keyframes via the API. For animation, use a Fusion `Transform` ([04](04-fusion-scripting.md) R6).
- Audio clip volume/pan are **not** exposed here.

---

## Transform

| Key | Type / Range | Notes |
|-----|--------------|-------|
| `Pan` | float, −4×width … 4×width | Horizontal position in pixels (0 = centered) |
| `Tilt` | float, −4×height … 4×height | Vertical position in pixels (positive = up) |
| `ZoomX` | float, 0.0 … 100.0 | 1.0 = 100% |
| `ZoomY` | float, 0.0 … 100.0 | |
| `ZoomGang` | bool | Lock X/Y zoom together |
| `RotationAngle` | float, −360 … 360 | Degrees |
| `AnchorPointX` | float, −4×width … 4×width | Rotation/scale pivot |
| `AnchorPointY` | float, −4×height … 4×height | |
| `Pitch` | float, −1.5 … 1.5 | 3D tilt-like perspective |
| `Yaw` | float, −1.5 … 1.5 | 3D swivel-like perspective |
| `FlipX` | bool | Horizontal flip |
| `FlipY` | bool | Vertical flip |

## Cropping

| Key | Type / Range |
|-----|--------------|
| `CropLeft` / `CropRight` | float, 0 … width (pixels) |
| `CropTop` / `CropBottom` | float, 0 … height (pixels) |
| `CropSoftness` | float, −100 … 100 |
| `CropRetain` | bool ("Retain Image Position") |

## Dynamic Zoom

| Key | Values |
|-----|--------|
| `DynamicZoomEase` | 0 `DYNAMIC_ZOOM_EASE_LINEAR`, 1 `_IN`, 2 `_OUT`, 3 `_IN_AND_OUT` |

(Turning Dynamic Zoom on and setting its start/end rectangles is UI-only.)

## Composite

| Key | Type |
|-----|------|
| `Opacity` | float, 0.0 … 100.0 |
| `CompositeMode` | enum, see below |

| Value | Constant | Value | Constant |
|------:|----------|------:|----------|
| 0 | `COMPOSITE_NORMAL` | 16 | `COMPOSITE_COLORIZE` |
| 1 | `COMPOSITE_ADD` | 17 | `COMPOSITE_LUMA_MASK` |
| 2 | `COMPOSITE_SUBTRACT` | 18 | `COMPOSITE_DIVIDE` |
| 3 | `COMPOSITE_DIFF` | 19 | `COMPOSITE_LINEAR_DODGE` |
| 4 | `COMPOSITE_MULTIPLY` | 20 | `COMPOSITE_LINEAR_BURN` |
| 5 | `COMPOSITE_SCREEN` | 21 | `COMPOSITE_LINEAR_LIGHT` |
| 6 | `COMPOSITE_OVERLAY` | 22 | `COMPOSITE_VIVID_LIGHT` |
| 7 | `COMPOSITE_HARDLIGHT` | 23 | `COMPOSITE_PIN_LIGHT` |
| 8 | `COMPOSITE_SOFTLIGHT` | 24 | `COMPOSITE_HARD_MIX` |
| 9 | `COMPOSITE_DARKEN` | 25 | `COMPOSITE_LIGHTER_COLOR` |
| 10 | `COMPOSITE_LIGHTEN` | 26 | `COMPOSITE_DARKER_COLOR` |
| 11 | `COMPOSITE_COLOR_DODGE` | 27 | `COMPOSITE_FOREGROUND` |
| 12 | `COMPOSITE_COLOR_BURN` | 28 | `COMPOSITE_ALPHA` |
| 13 | `COMPOSITE_EXCLUSION` | 29 | `COMPOSITE_INVERTED_ALPHA` |
| 14 | `COMPOSITE_HUE` | 30 | `COMPOSITE_LUM` |
| 15 | `COMPOSITE_SATURATE` | 31 | `COMPOSITE_INVERTED_LUM` |

> Integers follow the order in the official list (only `NORMAL = 0` is stated explicitly). If a value behaves unexpectedly, set the mode in the UI and read it back with `GetProperty("CompositeMode")`.

**Common uses:** Screen = light leaks, flares, and fire on black backgrounds. Multiply = textures/paper/dirt. Overlay/Soft Light = color washes and contrast textures. Add = glows. Luma Mask/Alpha = track mattes.

## Lens

| Key | Range |
|-----|-------|
| `Distortion` | float, −1.0 … 1.0 (negative fixes barrel distortion, e.g. GoPro) |

## Retime & Scaling

| Key | Values |
|-----|--------|
| `RetimeProcess` | 0 Use Project, 1 Nearest, 2 Frame Blend, 3 Optical Flow |
| `MotionEstimation` | 0 Use Project, 1 Standard Faster, 2 Standard Better, 3 Enhanced Faster, 4 Enhanced Better, 5 Speed Warp Better ⭐, 6 Speed Warp Faster ⭐ |
| `Scaling` | 0 Use Project, 1 Crop, 2 Fit, 3 Fill, 4 Stretch |
| `ResizeFilter` | 0 Use Project, 1 Sharper, 2 Smoother, 3 Bicubic, 4 Bilinear, 5 Bessel, 6 Box, 7 Catmull-Rom, 8 Cubic, 9 Gaussian, 10 Lanczos, 11 Mitchell, 12 Nearest Neighbor, 13 Quadratic, 14 Sinc, 15 Linear |

> `RetimeProcess` sets *how* frames are interpolated. It doesn't change the clip speed (no API for that).

---

## Other TimelineItem Controls

| Method | Purpose |
|--------|---------|
| `SetClipEnabled(bool)` / `GetClipEnabled()` | Enable/disable a clip |
| `SetClipColor("Orange")` / `ClearClipColor()` | Clip color label |
| `AddFlag("Red")` / `ClearFlags("All")` | Flags |
| `AddMarker(frame, color, name, note, duration, customData)` | Clip markers |
| `SetName(name)` | Rename the clip on the timeline |
| `GetStart()`, `GetEnd()`, `GetDuration()` | Timeline position (frames) |
| `GetSourceStartFrame()`, `GetSourceEndFrame()` | Source in/out |
| `GetLeftOffset()`, `GetRightOffset()` | Available handles |
| `GetLinkedItems()` | Linked audio/video items |
| `AddTake(...)`, `SelectTakeByIndex(i)`, `FinalizeTake()` | Take selector (alternate shots) |
| `timeline.DeleteClips([items], ripple=True)` | Delete / ripple-delete |
| `timeline.SetClipsLinked([items], True)` | Link/unlink |
| `timeline.CreateCompoundClip([items], {"name": "..."})` | Compound clip |
| `timeline.CreateFusionClip([items])` | Fusion clip from several items |

---

## Recipes

```python
W, H = 1920, 1080     # read real values: project.GetSetting("timelineResolutionWidth") / ("timelineResolutionHeight")

# Picture-in-picture, top-right, 30% size
pip.SetProperty({"ZoomX": 0.3, "ZoomY": 0.3, "Pan": W * 0.33, "Tilt": H * 0.33})

# Split screen left/right (two clips on V1/V2)
left.SetProperty({"CropRight": W / 2, "Pan": -W / 4});  right.SetProperty({"CropLeft": W / 2, "Pan": W / 4})
# (crop-and-shift keeps native scale; or use ZoomX 0.5 for a squeezed side-by-side)

# Mirror a selfie shot
item.SetProperty("FlipX", True)

# Light-leak overlay on V2
leak.SetProperty({"CompositeMode": 5, "Opacity": 70.0})     # Screen

# Static punch-in (crop-zoom for a second camera angle feel)
item.SetProperty({"ZoomX": 1.25, "ZoomY": 1.25, "Tilt": -40})

# Smooth slow motion quality (after the user sets the speed in the UI)
item.SetProperty({"RetimeProcess": 3, "MotionEstimation": 4})

# Fix GoPro distortion
item.SetProperty("Distortion", -0.3)

# Cinematic bars without cropping metadata: use Timeline → Output Blanking (UI), or
item.SetProperty({"CropTop": H * 0.12, "CropBottom": H * 0.12})
```
