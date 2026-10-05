# 08 — End-to-End Agent Workflows & Recipes

This guide provides complete, production-ready workflows for an AI agent controlling DaVinci Resolve. Each workflow combines API calls, workaround strategies (from [00-capability-matrix.md](00-capability-matrix.md)), and user guidance steps.

---

## Workflow 1: YouTube Talking-Head / Video Essay

**Goal:** Assemble an A-roll video, clean up voice, add B-roll picture-in-picture, generate auto-subtitles, and queue a YouTube render.

```
Step 1: Ingest & Organize ──► Step 2: Assemble Timeline ──► Step 3: Audio Cleanup
                                                                   │
Step 6: Render & Export  ◄── Step 5: Subtitles & Look  ◄── Step 4: B-Roll & Punch-in
```

### Scripted Automation (Python)

```python
import DaVinciResolveScript as dvr_script

resolve = dvr_script.scriptapp("Resolve")
pm = resolve.GetProjectManager()
project = pm.GetCurrentProject()
media_pool = project.GetMediaPool()
root = media_pool.GetRootFolder()

# 1. Create Bins & Ingest
bin_aroll = media_pool.AddSubFolder(root, "A-Roll")
bin_broll = media_pool.AddSubFolder(root, "B-Roll")
media_pool.SetCurrentFolder(bin_aroll)
aroll_clips = media_pool.ImportMedia(["/footage/talking_head_01.mp4"])

media_pool.SetCurrentFolder(bin_broll)
broll_clips = media_pool.ImportMedia(["/footage/broll_screen_demo.mp4"])

# 2. Build Base Timeline
timeline = media_pool.CreateEmptyTimeline("Main_Edit_v1")
project.SetCurrentTimeline(timeline)

# Append talking head to Track V1 / A1
media_pool.AppendToTimeline([{
    "mediaPoolItem": aroll_clips[0],
    "startFrame": 0,
    "endFrame": 2400,     # 100 seconds at 24fps
    "trackIndex": 1
}])

# 3. Clean Dialogue Audio (Studio Voice Isolation)
v1_items = timeline.GetItemListInTrack("video", 1)
a1_items = timeline.GetItemListInTrack("audio", 1)
if a1_items:
    # 65% Voice Isolation removes room AC / PC fan without sounding robotic
    a1_items[0].SetVoiceIsolationState({"isEnabled": True, "amount": 65})

# 4. Add B-Roll Cutaway on Track V2
timeline.AddTrack("video")
media_pool.SetCurrentFolder(bin_broll)
broll_timeline_items = media_pool.AppendToTimeline([{
    "mediaPoolItem": broll_clips[0],
    "startFrame": 120,
    "endFrame": 360,      # 10 seconds cutaway
    "trackIndex": 2,
    "recordFrame": 480    # Starts at 20s mark
}])

# Reframe B-roll as Picture-in-Picture (top-right corner)
if broll_timeline_items:
    pip = broll_timeline_items[0]
    pip.SetProperty({
        "ZoomX": 0.35,
        "ZoomY": 0.35,
        "Pan": 550.0,
        "Tilt": 300.0
    })

# 5. Insert Text+ Hook Title at 00:00:02:00
timeline.SetCurrentTimecode("01:00:02:00")
title_item = timeline.InsertFusionTitleIntoTimeline("Text+")
if title_item:
    comp = title_item.GetFusionCompByIndex(1)
    if comp:
        text_tool = comp.FindToolByID("TextPlus")
        if text_tool:
            text_tool.SetInput("StyledText", "HOW TO MASTER AI WORKFLOWS")
            text_tool.SetInput("Size", 0.075)
            text_tool.SetInput("Center", {1: 0.5, 2: 0.82})

# 6. Generate Auto-Subtitles (Studio)
timeline.CreateSubtitlesFromAudio({
    resolve.SUBTITLE_LANGUAGE: resolve.AUTO_CAPTION_ENGLISH,
    resolve.SUBTITLE_CAPTION_PRESET: resolve.AUTO_CAPTION_SUBTITLE_DEFAULT,
    resolve.SUBTITLE_CHARS_PER_LINE: 36,
    resolve.SUBTITLE_LINE_BREAK: resolve.AUTO_CAPTION_LINE_DOUBLE,
    resolve.SUBTITLE_GAP: 2
})

# 7. Setup YouTube 1080p Render
project.LoadRenderPreset("YouTube - 1080p")
project.SetRenderSettings({
    "TargetDir": "/exports/youtube/",
    "CustomName": "youtube_master_v1",
    "ExportSubtitle": True,
    "SubtitleFormat": "BurnIn"
})
job_id = project.AddRenderJob()
print(f"Render queued with ID: {job_id}")
```

---

## Workflow 2: Multi-Track Video Podcast

**Goal:** Sync separate microphone audio to camera video, apply Voice Isolation and Fairlight preset, add chapter markers, and export both full video and audio-only podcast master.

### Execution Blueprint

1. **Auto-Sync Footage via Waveform:**
   ```python
   # Select camera scratch clip + Zoom/Rode WAV clip
   media_pool.AutoSyncAudio([camera_mp_item, external_audio_mp_item], {
       resolve.AUDIO_SYNC_MODE: resolve.AUDIO_SYNC_WAVEFORM,
       resolve.AUDIO_SYNC_CHANNEL_NUMBER: resolve.AUDIO_SYNC_CHANNEL_AUTOMATIC,
       resolve.AUDIO_SYNC_RETAIN_EMBEDDED_AUDIO: False
   })
   ```

2. **Track Layout Standard:**
   * `Track V1`: Host Camera
   * `Track V2`: Guest Camera / Wide
   * `Track A1`: Host Mic (mono)
   * `Track A2`: Guest Mic (mono)
   * `Track A3`: Intro/Outro Music (stereo)

3. **Batch Dialogue Processing:**
   ```python
   # Apply Voice Isolation across all items on A1 & A2
   for track_idx in [1, 2]:
       timeline.SetVoiceIsolationState(track_idx, {"isEnabled": True, "amount": 60})

   # Apply studio Fairlight mastering preset
   project.ApplyFairlightPresetToCurrentTimeline("Podcast Master Chain")
   ```

4. **Chapter & Show-Note Markers:**
   ```python
   # Timeline markers exportable to YouTube description or show notes
   chapters = [
       (0, "Cyan", "Intro", "Welcome and sponsor shoutout"),
       (2880, "Blue", "Topic 1", "State of Open Source AI"),
       (8640, "Blue", "Topic 2", "Hardware benchmarks"),
       (14400, "Green", "Outro", "Final thoughts and links")
   ]

   for frame, color, title, note in chapters:
       timeline.AddMarker(frame, color, title, note, 1.0, "")
   ```

5. **Dual Export (Video + Audio Feed):**
   ```python
   # Job 1: Full Video
   project.SetRenderSettings({
       "TargetDir": "/exports/podcast/",
       "CustomName": "ep42_full_video",
       "ExportVideo": True,
       "ExportAudio": True
   })
   vid_job = project.AddRenderJob()

   # Job 2: Audio Only (MP3 / AAC for RSS feed)
   project.SetRenderSettings({
       "TargetDir": "/exports/podcast/",
       "CustomName": "ep42_audio_feed",
       "ExportVideo": False,
       "ExportAudio": True,
       "AudioCodec": "aac",
       "AudioSampleRate": 48000,
       "AudioBitDepth": 24
   })
   audio_job = project.AddRenderJob()

   project.StartRendering([vid_job, audio_job])
   ```

---

## Workflow 3: Social Media Vertical Format (Reels / TikTok / Shorts)

**Goal:** Convert horizontal 16:9 material into 9:16 vertical video (1080×1920), center subject via Smart Reframe, add fast-paced subtitles, and fill blanking areas.

### Scripted Pipeline

```python
# 1. Switch Timeline to Vertical Resolution
timeline.SetSetting("useCustomSettings", "1")
timeline.SetSetting("timelineResolutionWidth", "1080")
timeline.SetSetting("timelineResolutionHeight", "1920")

# 2. Reframe Talking Head for Vertical
v1_items = timeline.GetItemListInTrack("video", 1)
for item in v1_items:
    # Option A: Automatic AI Reframe (Studio)
    success = item.SmartReframe()

    # Option B: Manual fallback if SmartReframe fails
    if not success:
        # Scale up to fill vertical frame and center
        item.SetProperty({
            "Scaling": 3,      # Fill mode
            "ZoomX": 1.0,
            "ZoomY": 1.0,
            "Pan": 0.0,
            "Tilt": 50.0       # Shift slightly up to keep head in upper third
        })

# 3. High-Paced Short-Form Subtitles
# Vertical video reads best with 16-24 characters per line
timeline.CreateSubtitlesFromAudio({
    resolve.SUBTITLE_LANGUAGE: resolve.AUTO_CAPTION_ENGLISH,
    resolve.SUBTITLE_CAPTION_PRESET: resolve.AUTO_CAPTION_SUBTITLE_DEFAULT,
    resolve.SUBTITLE_CHARS_PER_LINE: 22,
    resolve.SUBTITLE_LINE_BREAK: resolve.AUTO_CAPTION_LINE_SINGLE,
    resolve.SUBTITLE_GAP: 0
})

# 4. Animated Hook Title (top zone safe from UI buttons)
timeline.SetCurrentTimecode("01:00:00:00")
hook = timeline.InsertFusionTitleIntoTimeline("Text+")
if hook:
    comp = hook.GetFusionCompByIndex(1)
    if comp:
        txt = comp.FindToolByID("TextPlus")
        txt.SetInput("StyledText", "DON'T MISS THIS 🚨")
        txt.SetInput("Size", 0.09)
        txt.SetInput("Center", {1: 0.5, 2: 0.78})  # Above platform overlays
```

> [!TIP]
> **Safe Margins for 9:16:** Avoid placing critical text in the **top 15%** (status bar & search header) and **bottom 25%** (username, caption, and audio tags). Keep text strictly between $Y = 0.25$ and $Y = 0.80$.

---

## Workflow 4: Narrative / Cinematic Post Pipeline

**Goal:** Ingest log footage, apply project color management (or CST), match shots via CDL, apply a cinematic film look (DRX), and export ProRes/DNxHR master.

### Workflow Sequence

```
Raw Media ──► Color Space Transform ──► Primary CDL Balance ──► DRX Look / Grain ──► ProRes Master
```

```python
# 1. Automatic Scene Cut Detection on long pre-cut footage
timeline = project.GetCurrentTimeline()
timeline.DetectSceneCuts()

# 2. Iterate Clips and Apply Unified Grade
video_clips = timeline.GetItemListInTrack("video", 1)
LOOK_DRX = "/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Looks/cinematic_35mm.drx"

# Create a Shared Color Group for Scene 1
scene_group = project.AddColorGroup("Scene_01_Interior")

for idx, clip in enumerate(video_clips):
    # Assign to group
    clip.AssignToColorGroup(scene_group)
    
    # Mild primary balance per clip (warmer skin, balanced shadows)
    clip.SetCDL({
        "NodeIndex": "1",
        "Slope": "1.02 1.00 0.97",
        "Offset": "0.005 0.000 -0.005",
        "Power": "1.00 1.00 1.00",
        "Saturation": "1.05"
    })

# Apply film look to group post-clip node graph (affects all scene clips)
post_graph = scene_group.GetPostClipNodeGraph()
post_graph.ApplyGradeFromDRX(LOOK_DRX, 0)

# 3. Master Export Configuration (ProRes 422 HQ)
project.SetRenderSettings({
    "TargetDir": "/masters/deliverables/",
    "CustomName": "film_master_prores422hq",
    "ExportVideo": True,
    "ExportAudio": True,
    "AudioCodec": "lpcm",
    "AudioBitDepth": 24,
    "AudioSampleRate": 48000
})
project.SetCurrentRenderFormatAndCodec("mov", "ProRes422HQ")
job = project.AddRenderJob()
```

---

## Workflow 5: Agent Safety & Error-Recovery Checklist

When building an autonomous AI agent or MCP server, always implement this defensive guardrail pattern before executing commands:

### The Defensive Execution Pattern

```python
def safe_agent_execute(operation_name, func, *args, **kwargs):
    """
    Wraps Resolve operations with:
    1. Session validation
    2. Non-destructive backup (Save & Duplicate)
    3. Return value verification
    """
    resolve = dvr_script.scriptapp("Resolve")
    if not resolve:
        return {"status": "error", "message": "DaVinci Resolve is not running or External Scripting is disabled."}

    pm = resolve.GetProjectManager()
    project = pm.GetCurrentProject()
    if not project:
        return {"status": "error", "message": "No active project open in DaVinci Resolve."}

    timeline = project.GetCurrentTimeline()
    if not timeline:
        return {"status": "error", "message": "No active timeline selected."}

    # Safe checkpoint: Duplicate timeline before destructive batch operations
    if kwargs.pop("create_checkpoint", False):
        curr_name = timeline.GetName()
        checkpoint = timeline.DuplicateTimeline(f"{curr_name}_agent_backup")
        if checkpoint:
            print(f"[Safety Checkpoint] Duplicated '{curr_name}' -> '{curr_name}_agent_backup'")

    # Execute
    try:
        result = func(resolve, project, timeline, *args, **kwargs)
        # Always persist progress
        pm.SaveProject()
        return {"status": "success", "result": result}
    except Exception as e:
        return {"status": "failed", "error": str(e), "operation": operation_name}
```

### Common Error Codes & Mitigations

| Error Symptom | Root Cause | Agent Action |
|:---|:---|:---|
| `scriptapp("Resolve")` returns `None` | Resolve closed OR External Scripting not enabled | Prompt user to launch Resolve Studio and verify **Preferences > General > External Scripting = Local**. |
| `InsertFusionTitleIntoTimeline` returns `None` | Template name typo or version difference | Query installed templates or fall back to standard `"Text+"`. |
| `CreateSubtitlesFromAudio` returns `False` | Studio language pack extras not installed | Prompt user to open **DaVinci Resolve Studio menu > Extras Download Manager** and install voice models. |
| `SetProperty` doesn't alter clip | Clip is audio-only or property key misspelled | Inspect `item.GetProperty()` to verify supported keys on target item. |
| Playhead moves but item inserted on wrong track | Track destination targeting in Resolve GUI | Call `timeline.GetTrackCount("video")`, add a dedicated track, and verify item placement with `item.GetTrackTypeAndIndex()`. |
| Render fails immediately | Target directory does not exist or disk permissions | Validate `os.path.isdir(TargetDir)` before calling `AddRenderJob()`. |

---

## Quick Reference Summary for LLM Agents

* **Always check 1-based indexing:** Tracks, nodes, and takes are $1, 2, 3...$
* **Normalized coordinates:** In Fusion, $\{1: 0.5, 2: 0.5\}$ is dead-center.
* **Inspect before guessing:** Call `item.GetProperty()` or `tool.GetInputList()` dynamically.
* **Never leave the user blocked:** If an operation is tier 🔴 (UI-only), return clear step-by-step click paths immediately.
