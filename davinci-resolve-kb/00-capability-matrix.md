# 00 — Capability Matrix: What the Agent Can and Cannot Do

This is the most important file. Before promising the user anything, check which tier the request falls into.

- 🟢 **Direct API**: one or a few API calls, reliable
- 🟡 **Workaround**: possible through an indirect technique (DRX, Fusion, interchange files, external tools)
- 🔴 **UI-only**: no scripting path; the agent must guide the user with click paths (or use OS-level UI automation, which is fragile)

> [!IMPORTANT]
> The scripting API has **no** function such as `AddEffect`, `AddTransition`, `AddFairlightFX`, `SetVolume`, or `SetSpeed`. Do not invent them. (Correction to an earlier note: `SetDialogueLeveler` does **not** exist in the API either.)

---

## Video Effects (Resolve FX / OpenFX)

| Task | Tier | How |
|------|------|-----|
| Drag a Resolve FX (e.g. Glow) onto a clip on the Edit page | 🔴 | No API. Guide the user, or use the workarounds below |
| Apply a Resolve FX through a **color node** | 🟡 | Pre-build a grade containing the effect, save it as a still/DRX, then `graph.ApplyGradeFromDRX(path, 0)` |
| Apply an effect through **Fusion** | 🟡 | `item.AddFusionComp()` or `ImportFusionComp(path)`, then add Fusion tools (Blur, Glow, FilmGrain…) with `comp.AddTool()` |
| Enable/disable a color node (toggle an effect on/off) | 🟢 | `graph.SetNodeEnabled(nodeIndex, bool)` |
| List tools used in a node | 🟢 | `graph.GetToolsInNode(nodeIndex)` |
| Stabilize a clip | 🟢 | `item.Stabilize()` |
| Smart Reframe (Studio) | 🟢 | `item.SmartReframe()` |
| Magic Mask (Studio) | 🟢 | `item.CreateMagicMask("F" / "B" / "BI")`, `RegenerateMagicMask()` |
| Remove motion blur (Studio, AI) | 🟢 | `mediaPoolItem.RemoveMotionBlur({...})` (creates a new clip) |
| Super Scale upscaling | 🟢 | `mediaPoolItem.SetClipProperty("Super Scale", 2)` |
| Scene cut detection | 🟢 | `timeline.DetectSceneCuts()` |
| Render-cache Fusion/Color output | 🟢 | `item.SetFusionOutputCache(...)`, `SetColorOutputCache(...)` |

## Transform / Inspector

| Task | Tier | How |
|------|------|-----|
| Zoom, position, rotate, flip, crop, opacity, blend mode | 🟢 | `item.SetProperty(key, value)`, see [07](07-inspector-properties.md) |
| Ken Burns / dynamic zoom ease | 🟢/🟡 | `SetProperty("DynamicZoomEase", n)` sets the ease; enabling Dynamic Zoom itself is UI-only |
| **Keyframe** Inspector values over time | 🔴/🟡 | Not exposed for Edit-page Inspector. Use a Fusion `Transform` tool with keyframes instead |
| Retime quality (optical flow, etc.) | 🟢 | `SetProperty("RetimeProcess", 3)` |
| **Change clip speed** (e.g. 50%) | 🔴/🟡 | No API. Workaround: FCPXML round-trip with a timeMap, or UI (`R` → Change Clip Speed) |
| Lens distortion | 🟢 | `SetProperty("Distortion", -1.0..1.0)` |

## Transitions

| Task | Tier | How |
|------|------|-----|
| Add a Cross Dissolve / any transition | 🔴/🟡 | No API. Workaround: export FCPXML/OTIO, inject transitions, re-import with `mediaPool.ImportTimelineFromFile()`. Or guide: select edit points → `Ctrl/Cmd+T` |
| Fade in/out of a clip | 🟡 | Fusion comp with keyframed `Merge.Blend` or `BrightnessContrast.Gain`; or UI fade handles |

## Titles, Graphics, Generators

| Task | Tier | How |
|------|------|-----|
| Insert a basic title | 🟢 | `timeline.InsertTitleIntoTimeline("Text")` |
| Insert a Fusion title (Text+ or template) | 🟢 | `timeline.InsertFusionTitleIntoTimeline("Text+")` |
| Insert a generator (Solid Color, bars…) | 🟢 | `timeline.InsertGeneratorIntoTimeline("Solid Color")` |
| Insert a Fusion generator | 🟢 | `timeline.InsertFusionGeneratorIntoTimeline(name)` |
| Insert an OFX generator | 🟢 | `timeline.InsertOFXGeneratorIntoTimeline(name)` |
| Insert an empty Fusion composition | 🟢 | `timeline.InsertFusionCompositionIntoTimeline()` |
| **Change the text** of a title | 🟢 (Fusion) | `item.GetFusionCompByIndex(1)` → find the `TextPlus` tool → `SetInput("StyledText", "...")` |
| Build custom motion graphics | 🟢 | Fusion scripting, see [04](04-fusion-scripting.md) |
| Import a Fusion template/macro | 🟢 | `item.ImportFusionComp("/path/file.comp")` |
| Auto-subtitles from speech (Studio) | 🟢 | `timeline.CreateSubtitlesFromAudio({...})` |
| Burn subtitles into the render | 🟢 | `project.SetRenderSettings({"ExportSubtitle": True, "SubtitleFormat": "BurnIn"})` |
| Style subtitles (font, size, box) | 🔴 | UI: Subtitle track → Inspector → Track Style |

> Insert functions place the item **at the playhead on the current/selected track**. Set the playhead first with `timeline.SetCurrentTimecode("01:00:05:00")`.

## Audio

| Task | Tier | How |
|------|------|-----|
| Voice Isolation on a clip (Studio) | 🟢 | `item.SetVoiceIsolationState({"isEnabled": True, "amount": 70})` |
| Voice Isolation on a whole track (Studio) | 🟢 | `timeline.SetVoiceIsolationState(trackIndex, {...})` |
| Auto-sync audio to video | 🟢 | `mediaPool.AutoSyncAudio([items], {...})` |
| Transcribe audio (Studio) | 🟢 | `mediaPoolItem.TranscribeAudio()` / `folder.TranscribeAudio()` |
| Classify audio (dialogue/music/SFX) | 🟢 | `mediaPoolItem.PerformAudioClassification()` |
| AI text-to-speech (Studio + Extras) | 🟢 | `project.GenerateSpeech({...}, timecode)` |
| Insert audio at playhead on Fairlight | 🟢 | `project.InsertAudioToCurrentTrackAtPlayhead(path, offset, duration)` |
| Add tracks (mono/stereo/5.1…) | 🟢 | `timeline.AddTrack("audio", "stereo")` |
| Apply a Fairlight preset | 🟢 | `project.ApplyFairlightPresetToCurrentTimeline(name)` |
| **Clip volume / track fader / pan** | 🔴 | No API. Workaround: pre-process with ffmpeg and re-import, or guide the user |
| Add EQ, compressor, De-Esser, Reverb… | 🔴/🟡 | No API. Workaround: save a Fairlight **preset** with the track FX in the UI once, then apply it via API; or pre-process externally |
| Normalize loudness | 🔴/🟡 | UI: right-click clip → Normalize Audio Levels. Or ffmpeg `loudnorm` before import |
| Dialogue Leveler, Ducking, Music Remixer | 🔴 | UI-only (Inspector / Fairlight) |
| Mute/lock a track | 🟢 | `timeline.SetTrackEnable("audio", i, False)`, `SetTrackLock(...)` |

## Color

| Task | Tier | How |
|------|------|-----|
| Primary correction via CDL | 🟢 | `item.SetCDL({...})` |
| Apply a LUT to a node | 🟢 | `item.GetNodeGraph().SetLUT(nodeIndex, path)` |
| Apply a saved grade / look | 🟢 | `graph.ApplyGradeFromDRX(path, 0)` |
| Copy a grade to other clips | 🟢 | `item.CopyGrades([targets])` |
| Color groups (pre/post clip) | 🟢 | `project.AddColorGroup()`, `item.AssignToColorGroup(g)` |
| Versions (A/B looks) | 🟢 | `item.AddVersion("Warm", 0)`, `LoadVersionByName(...)` |
| Reset grades | 🟢 | `graph.ResetAllGrades()` |
| Export a LUT from a grade | 🟢 | `item.ExportLUT(resolve.EXPORT_LUT_33PTCUBE, path)` |
| Add nodes, curves, qualifiers, windows | 🔴/🟡 | No API to create nodes. Build in UI → save DRX → apply via API |

## Delivery

| Task | Tier | How |
|------|------|-----|
| Render with preset/settings | 🟢 | `LoadRenderPreset`, `SetRenderSettings`, `AddRenderJob`, `StartRendering` |
| Quick Export (YouTube etc.) | 🟢 | `project.RenderWithQuickExport(preset, {...})` |
| Render audio only | 🟢 | `SetRenderSettings({"ExportVideo": False, "ExportAudio": True})` |

---

## Workaround Techniques in Detail

### W1 — The "Look Library" (DRX) technique for Resolve FX
The most reliable way to apply Resolve FX by script.

1. In the Color page, build a node tree containing the effects (e.g. Node 1: Glow, Node 2: Film Grain, Node 3: Vignette window).
2. Right-click the viewer → **Grab Still**, then in the Gallery right-click the still → **Export** → `.drx`.
3. Store it in a library folder, e.g. `~/ResolveLooks/glow_grain_vignette.drx`.
4. The agent applies it:
   ```python
   graph = item.GetNodeGraph()
   graph.ApplyGradeFromDRX("/Users/me/ResolveLooks/glow_grain_vignette.drx", 0)
   ```
5. To toggle a single effect later: `graph.SetNodeEnabled(2, False)`.

> [!NOTE]
> `ApplyGradeFromDRX` **replaces** the clip's current grade. If the clip already has a correction, put the correction inside the DRX too, or use a color group post-clip graph for the look.

### W2 — Fusion comp per clip
Every timeline clip can carry Fusion compositions. Fusion has native tools for blur, glow, grain, color, transforms, text, masks, and keyframes. See [04-fusion-scripting.md](04-fusion-scripting.md).

### W3 — Fusion templates
Build a `.comp` or `.setting` once in Fusion, save it, then `item.ImportFusionComp(path)` and change only the inputs (text, colors).

### W4 — Timeline interchange round-trip
For transitions and speed changes:
1. `timeline.Export(path, resolve.EXPORT_FCPXML_1_10, resolve.EXPORT_NONE)`
2. Edit the XML (add `<transition>` elements or timeMaps)
3. `mediaPool.ImportTimelineFromFile(path, {"timelineName": "v2_with_transitions"})`

Caveats: only standard transitions (mainly Cross Dissolve) survive the round-trip reliably, and some Resolve-specific attributes are lost. Always import as a **new** timeline.

### W5 — External pre-processing (audio)
For loudness, EQ, and compression without UI access, process the source with ffmpeg, then import:
```bash
ffmpeg -i in.wav -af "highpass=f=80,acompressor=threshold=-18dB:ratio=3:attack=10:release=150,loudnorm=I=-14:TP=-1:LRA=11" out.wav
```
Then `mediaPool.ImportMedia(["/path/out.wav"])` or `mpItem.ReplaceClip("/path/out.wav")`.

### W6 — Fairlight presets
In the UI, set up track FX, EQ, and dynamics once, then save them as a Fairlight preset. Afterwards the agent can call `resolve.GetFairlightPresets()` and `project.ApplyFairlightPresetToCurrentTimeline(name)`. The API reference doesn't document exactly what a preset stores, so test once that it restores the processing you need.

### W7 — UI guidance (fallback)
When nothing else works, give the user exact steps: page → panel → control → value. Each catalog file includes click paths.

---

## Suggested MCP Tools (Effects/Audio/Graphics Layer)

| Tool | Wraps |
|------|-------|
| `apply_look(clip_ref, look_name)` | W1 (DRX library) |
| `toggle_node(clip_ref, node_index, enabled)` | `Graph.SetNodeEnabled` |
| `set_transform(clip_ref, {Pan, Tilt, ZoomX, ...})` | `TimelineItem.SetProperty` |
| `add_fusion_effect(clip_ref, effect, params)` | W2 |
| `insert_title(text, timecode, duration, style)` | `InsertFusionTitleIntoTimeline` + Fusion `StyledText` |
| `add_lower_third(name, role, timecode)` | W3 template |
| `voice_isolation(target, amount)` | `SetVoiceIsolationState` |
| `generate_subtitles(language, preset)` | `CreateSubtitlesFromAudio` |
| `preprocess_audio(path, target_lufs)` | W5 |
| `stabilize / smart_reframe / magic_mask(clip_ref)` | Direct API |
| `ui_instructions(task)` | Returns click paths from this knowledge base |
