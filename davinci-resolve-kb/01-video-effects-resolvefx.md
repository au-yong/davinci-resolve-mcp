# 01 — Video Effects: Resolve FX / OpenFX Catalog

**Where:** Effects Library → **OpenFX → Filters** (Edit/Cut pages), or **OpenFX panel** on the Color page (applied to a node). Fusion has a separate tool set, see [04](04-fusion-scripting.md).

**Legend:** ⭐ = DaVinci Resolve **Studio** only (adds a watermark in the free version). Studio status changes between versions, so if unsure, tell the user it *may* require Studio.

> [!IMPORTANT]
> **Automation:** Resolve FX cannot be added by API directly. Use the DRX look library (W1) or Fusion equivalents (W2) from [00-capability-matrix.md](00-capability-matrix.md). The Fusion equivalent column gives the closest Fusion tool ID for scripting.

> Library categories are approximate and differ by version. Tell users to type the effect name into the Effects Library **search** box.

---

## 1. Blur

| Effect | Use it for | Key parameters (typical start values) | Fusion equivalent |
|--------|-----------|----------------------------------------|-------------------|
| **Gaussian Blur** | Soften, blur backgrounds, privacy blur with a window | Strength 0.3–0.6; H/V ratio | `Blur` |
| **Box Blur** | Fast, slightly blocky blur | Strength, iterations | `Blur` (Filter = Box) |
| **Directional Blur** | Motion streak in one direction | Angle, length | `DirectionalBlur` |
| **Radial Blur** | Spin blur around a center | Center, angle | `DirectionalBlur` (Type = Radial) |
| **Zoom Blur** | Punch-in energy, speed effect | Center, amount 0.1–0.3 | `DirectionalBlur` (Type = Zoom) |
| **Lens Blur** ⭐ | Realistic bokeh / shallow depth of field | Iris shape, radius | `Defocus` |
| **Mosaic Blur** | Pixelate faces or plates | Pixel size | Not native; use `Resize` down then up |
| **Prism Blur** | Chromatic, dreamy blur | Strength, color spread | — |

**Blur a face or plate:** Color page → node → Power Window (circle) → Tracker → add Gaussian Blur or Mosaic to the node. Or Edit page → Effects → **Face/Object Blur** style workflows via a Fusion `EllipseMask` + `Blur`.

## 2. Color

| Effect | Use it for | Key parameters |
|--------|-----------|----------------|
| **Color Space Transform** | Convert log → Rec.709 (e.g. S-Log3 → Rec.709) | Input/Output Color Space, Gamma, Tone Mapping |
| **Film Look Creator** ⭐ | Complete film emulation (halation, bloom, grain, gate weave) | Preset, exposure, film stock, grain |
| **Color Stabilizer** ⭐ | Remove color/exposure drift within a shot | Analysis, smoothing |
| **Color Compressor** | Pull hues toward a target (e.g. unify skin tones) | Target hue, range, strength |
| **Color Generator** | Solid color overlay | Color |
| **Contrast Pop** | Local contrast punch | Amount 0.2–0.5 |
| **Chromatic Adaptation** | White balance in the correct color space | Illuminant |
| **Invert Color** | Negative image | Channels |
| **DCTL** | Run custom DCTL color scripts | DCTL file |
| **Gamut Mapping / Gamut Limiter** | Keep colors broadcast/gamut legal | Target gamut |
| **False Color** | Exposure check overlay | Mode |

## 3. Light

| Effect | Use it for | Key parameters (start values) |
|--------|-----------|-------------------------------|
| **Glow** | Highlights bloom, dreamy look | Shine threshold 0.7–0.85, Spread, Gain 0.3–0.6 |
| **Aperture Diffraction** ⭐ | Realistic starburst on bright points | Iris shape, blades |
| **Lens Flare** ⭐ | Synthetic lens flare | Preset, position (trackable) |
| **Lens Reflections** ⭐ | Ghosting reflections from bright sources | Threshold, intensity |
| **Light Rays** ⭐ | God rays streaming from highlights | Source position, length |
| **Halation** ⭐ | Red/orange edge glow typical of film | Threshold, spread, tint |
| **Relight** ⭐ (DNE) | Add virtual light sources using a depth map | Light type, position, intensity |
| **Soft Glow** | Gentle diffusion | Threshold, spread |

## 4. Refine / Beauty

| Effect | Use it for | Key parameters |
|--------|-----------|----------------|
| **Beauty** ⭐ | Skin smoothing (classic) | Operation mode, smoothing 0.2–0.4 |
| **Ultra Beauty** ⭐ | Higher-quality skin retouch | Smoothing, detail recovery |
| **Face Refinement** ⭐ (DNE) | Track face; adjust eyes, lips, cheeks, blemishes | Analyze → per-feature sliders |
| **Skin Refinement** | Skin texture balancing | Amount |
| **Noise Reduction** ⭐ (Color page) | Temporal + spatial denoise | Temporal frames 2–3, Spatial threshold 5–15 |
| **UltraNR** ⭐ (DNE) | AI spatial denoise | Mode, strength |
| **Detail Enhancer** | Recover fine texture | Amount |

## 5. Revival (Restoration)

| Effect | Use it for | Notes |
|--------|-----------|-------|
| **Dead Pixel Fixer** | Hot/stuck sensor pixels | Click to mark pixels |
| **Deflicker** ⭐ | Timelapse flicker, LED/fluorescent flicker | Preset: Timelapse / Fluro Light |
| **Dust Buster** ⭐ | Remove dust/dirt on scanned film | Auto / manual click |
| **Automatic Dirt Removal** ⭐ | Temporal dirt cleanup | Motion estimation |
| **Patch Replacer** ⭐ | Clone over small objects (logos, blemishes) | Source/target patch, tracking |
| **Object Removal** ⭐ (DNE) | Remove moving objects using clean-plate analysis | Needs Magic Mask/Window + Scene Analysis |
| **Chromatic Aberration Removal** | Fix purple/green fringes | Strength |
| **Frame Replacer** | Replace a bad frame with an interpolated one | Mode |
| **Despeckle / Dust & Scratch** | Film grain artifacts | Threshold |

## 6. Sharpen

| Effect | Use it for | Key parameters |
|--------|-----------|----------------|
| **Sharpen** | General sharpening | Amount 0.1–0.3 (avoid halos) |
| **Sharpen Edges** | Edge-only sharpening | Edge threshold |
| **Soften & Sharpen** | Separate small/medium/large texture control | Texture bands |

## 7. Stylize

| Effect | Use it for |
|--------|-----------|
| **Vignette** | Darken edges to draw focus (Size 0.6–0.8, Softness 0.5+) |
| **Film Grain** ⭐ | Organic texture (Grain size 35mm/16mm, strength low) |
| **Film Damage** ⭐ | Scratches, dirt, flicker for vintage looks |
| **Scanlines** | CRT / monitor screen look |
| **Analog Damage** ⭐ | VHS/broadcast glitch, noise, color bleed |
| **Blanking Fill** ⭐ | Fill letterbox bars with blurred image (vertical video in 16:9) |
| **Abstraction / Watercolor / Pencil Sketch / Edge Detect** | Artistic looks |
| **Emboss / Mirrors / Kaleidoscope** | Stylized geometry |
| **Prism / Glitch / Digital Glitch** | Glitch transitions or accents |
| **Stop Motion** | Choppy frame-rate look |
| **JPEG Damage** ⭐ | Compression artifact look |
| **Drop Shadow** | Shadow behind keyed graphics/logos |
| **Letterbox / Blanking** | Cinematic bars (prefer Timeline → Output Blanking for whole timeline) |

## 8. Temporal

| Effect | Use it for |
|--------|-----------|
| **Motion Trails** | Ghost trails behind moving subjects |
| **Smear** | Temporal smear |
| **Deflicker** ⭐ | See Revival |

## 9. Transform / Warp

| Effect | Use it for | Notes |
|--------|-----------|-------|
| **Transform** | Position/scale/rotate inside a node | Inspector is simpler on the Edit page |
| **Camera Shake** | Handheld or impact shake | Motion scale, speed, randomness |
| **Video Collage** | Grid / split-screen layouts | Tile count, spacing, borders |
| **Lens Distortion / Lens Correction** | Fix GoPro/wide-angle barrel distortion | Distortion amount |
| **Mirror** | Mirror along an axis | Angle |
| **Warper** ⭐ | Mesh/shape warping (slim, reshape) | Pin points |
| **Ripple / Vortex / Waves** | Liquid distortion | Amplitude, frequency |
| **Dent** | Bulge/pinch | Strength, center |

## 10. Key (Compositing)

| Effect | Use it for |
|--------|-----------|
| **3D Keyer** | Green/blue screen keying (Color page, high quality) |
| **HSL / Luma Keyer** | Key by hue/luminance |
| **Alpha Matte Shrink and Grow** | Clean matte edges |
| **Magic Mask** ⭐ (DNE) | AI isolation of people/objects (API: `CreateMagicMask`) |
| **Depth Map** ⭐ (DNE) | Generate a depth matte for fog, relight, focus |
| **Background removal (via Magic Mask)** ⭐ | Remove background without a green screen |

> Edit page also has **Ultra Keyer** / **Delta Keyer** inside Fusion (`UltraKeyer`, `DeltaKeyer`) for scripted keying.

## 11. Generate

| Effect | Use it for |
|--------|-----------|
| **Color Palette** | Extract palette swatches |
| **Grid** | Layout/safe-area guides |
| **Noise / Fast Noise** | Textures, fog, background motion |
| **Gradient** | Sky gradients, color washes |

---

## Quick Look Recipes (What to Combine)

| Look | Chain (node order on Color page) |
|------|----------------------------------|
| **Cinematic film** | CST (log→709) → primary balance → contrast S-curve → Halation ⭐ → Film Grain ⭐ (low) → Vignette |
| **Dreamy / wedding** | Balance → Glow (low gain) → Soft Glow → slight warm tint → Vignette |
| **Music video glitch** | Analog Damage ⭐ / Digital Glitch keyframed on beats → Prism Blur on accents |
| **Vintage VHS** | Lower saturation → Scanlines → Analog Damage ⭐ → Blur slight → 4:3 crop |
| **Documentary clean** | CST → balance → Contrast Pop (0.2) → Noise Reduction ⭐ → Sharpen (0.1) |
| **Interview skin** | Balance → Face Refinement ⭐ or Beauty (low) → qualifier for skin hue |
| **Vertical video in 16:9** | Blanking Fill ⭐, or duplicate clip on V1, scale up + Gaussian Blur, original on V2 |

---

## UI Click Paths (for guiding the user)

- **Apply to a clip (Edit page):** Effects (top-left) → Toolbox/OpenFX → drag effect onto the clip → adjust in Inspector → **Effects** tab.
- **Apply to a node (Color page):** select node → OpenFX panel (top-right) → drag effect onto node → Settings tab.
- **Track a window for a localized effect:** Color page → Window palette → draw shape → Tracker palette → Track Forward/Backward.
- **Copy effect to other clips:** Edit page → select clip → `Cmd/Ctrl+C` → select targets → `Option/Alt+V` (Paste Attributes) → choose Plugins.
