# 05 — Audio: Fairlight FX, Mixing, Loudness & Audio APIs

**Where:** Fairlight page (full mixer), Edit page Inspector → **Audio** tab (clip-level volume, pan, pitch, EQ, Voice Isolation, Dialogue Leveler), Effects → **Audio FX → Fairlight FX**.

> [!IMPORTANT]
> **Automation:** The API **cannot** set volume, pan, EQ, or dynamics, or add Fairlight FX. It **can** do Voice Isolation, audio sync, transcription, classification, AI speech, track creation, Fairlight presets, and audio-only renders. See section 6, and workarounds W5/W6 in [00](00-capability-matrix.md).

---

## 1. Clip-Level Controls (Edit page → Inspector → Audio)

| Control | What it does | Typical setting |
|---------|-------------|-----------------|
| **Volume** | Clip gain in dB | Dialogue peaks about −10 to −6 dBFS |
| **Pan** | L/R position | Dialogue center; ambience spread |
| **Pitch** | Semitones/cents shift | ±1–2 semitones for subtle voice change |
| **Speed** (Change Clip Speed) | Retime with or without pitch correction | — |
| **EQ** (4-band clip EQ) | Quick tonal fixes | See EQ cheat sheet |
| **Voice Isolation** ⭐ | AI removal of background noise/music | 50–80; 100 can sound processed |
| **Dialogue Leveler** ⭐ | Auto-evens loud/quiet speech | Moderate; check for pumping |
| **Normalize Audio Levels** (right-click clip) | Set peak or loudness target | Sample Peak −3 dBFS or ITU-R BS.1770 −14/−23 LUFS |
| **Fade handles** (on the clip) | Fade in/out | 2–10 frames at every cut to prevent clicks |

## 2. Fairlight Mixer Channel Strip (per track)

Order of processing (top to bottom): **Input → Effects inserts → EQ → Dynamics → Pan → Fader → Bus sends**.

| Section | Contents |
|---------|----------|
| **EQ** | 6-band parametric EQ with high-pass/low-pass filters |
| **Dynamics** | Expander/Gate, Compressor, Limiter, with sidechain |
| **Effects** | Insert slots for Fairlight FX, VST/AU plugins |
| **Pan** | Stereo/surround/3D panner |
| **Fader** | Track level, with automation (Read/Touch/Latch/Write) |
| **Bus** | Route tracks to sub-mixes (Dialogue / Music / SFX buses) and the Main |

---

## 3. Fairlight FX Catalog

⭐ = Studio only. Names as in Effects → Audio FX → Fairlight FX (may vary by version).

### Repair & Cleanup
| Effect | Purpose | Key parameters & starting values |
|--------|---------|----------------------------------|
| **Voice Isolation** ⭐ (Inspector / track) | AI isolation of dialogue from noise and music | Amount 50–80 |
| **Dialogue Separator** ⭐ | Split voice / background / reverb into separate levels | Voice +, Background −, Ambience − |
| **Noise Reduction** | Spectral denoise (constant hiss/hum) | Auto speech mode, or Learn on a noise-only section; threshold just above the noise floor |
| **De-Hummer** | Remove 50/60 Hz mains hum and harmonics | Frequency 50 (EU/Asia) or 60 (US); harmonics 4–8 |
| **De-Esser** | Tame harsh S/Sh sounds | Frequency 5–8 kHz; reduction 3–6 dB |
| **Dialogue Processor** | All-in-one voice strip: De-Rumble, De-Pop, De-Ess, Compressor, Expander, Exciter | Enable modules as needed |
| **Vocal Channel** | Simple channel strip: HPF + EQ + compressor | HPF 80–100 Hz; ratio 3:1 |
| **Stereo Fixer** | Fix channel/phase problems (e.g. dual-mono, swapped L/R) | Mode |
| **Soft Clipper** | Gently round off peaks | Ceiling −1 dB |

### Dynamics
| Effect | Purpose | Starting values |
|--------|---------|-----------------|
| **Compressor** (mixer Dynamics) | Even out level | Threshold −20 dB, ratio 3:1, attack 10–20 ms, release 100–200 ms, gain reduction 3–6 dB |
| **Multiband Compressor** | Frequency-specific compression | Tame boomy lows or harsh highs independently |
| **Limiter** | Hard ceiling, final protection | Ceiling −1 dBTP (streaming), −2 dBTP (some broadcast) |
| **Expander / Gate** | Reduce noise between words | Threshold just above the noise floor; range −10 to −20 dB (avoid hard gating) |

### Space & Time
| Effect | Purpose | Starting values |
|--------|---------|-----------------|
| **Reverb** | Add room/space | Small room for ADR matching; hall for music; mix 10–25% |
| **Delay** | Echo/slapback | 80–150 ms slapback; tempo-synced for music |
| **Echo** | Repeating decaying echo | Feedback 20–40% |

### Modulation & Creative
| Effect | Purpose |
|--------|---------|
| **Chorus** | Thicken/widen |
| **Flanger** | Sweeping jet effect |
| **Modulation** | Tremolo/vibrato-style effects |
| **Pitch** | Pitch shift (robot/monster voices, corrections) |
| **Distortion** | Telephone, radio, megaphone, lo-fi (combine with a band-pass EQ 300 Hz–3 kHz) |
| **Music Remixer** ⭐ (Inspector) | AI stem separation of music: voice / drums / bass / guitar / other levels |
| **Foley Sampler** | Trigger and record foley samples |

### Stereo & Metering
| Effect | Purpose |
|--------|---------|
| **Stereo Width** | Narrow or widen the stereo image |
| **Frequency Analyzer** | Real-time spectrum display |
| **Phase Meter** | Mono compatibility check |
| **Meter Bridge** / Loudness meter | Monitor levels and LUFS |
| **Surround Analyzer** | Surround field visualization |

---

## 4. EQ Cheat Sheet (Voice)

| Frequency | Character | Action |
|-----------|-----------|--------|
| < 80 Hz | Rumble, handling noise, AC | **High-pass** at 80–100 Hz (male), 100–120 Hz (female) |
| 100–250 Hz | Warmth/body; boominess if excessive | Cut 2–3 dB if boomy/proximity effect |
| 200–500 Hz | Mud, boxiness (small rooms) | Cut 2–4 dB with a medium Q |
| 800 Hz–1.5 kHz | Nasal, honky | Small cut if nasal |
| 2–5 kHz | Presence, intelligibility | Boost 1–3 dB for clarity |
| 5–8 kHz | Sibilance | De-ess here; don't boost |
| 10–16 kHz | Air, sparkle | Gentle shelf +1–2 dB |

**Music under dialogue:** cut 1–4 kHz on the music bus by 2–4 dB (makes space for speech), in addition to lowering the level.

---

## 5. Loudness & Level Targets

| Platform / Standard | Integrated loudness | True peak |
|---------------------|---------------------|-----------|
| YouTube, Spotify-style streaming | −14 LUFS | −1 dBTP |
| Apple Podcasts / podcasts | −16 LUFS (stereo) | −1 dBTP |
| Instagram / TikTok / Reels | about −14 LUFS | −1 dBTP |
| EBU R128 broadcast (Europe/Asia) | −23 LUFS (±0.5) | −1 dBTP |
| ATSC A/85 broadcast (US) | −24 LKFS | −2 dBTP |
| Netflix dialogue-gated | −27 LKFS (dialogue) | −2 dBTP |
| Cinema | No LUFS target; mix calibrated to 85 dB SPL reference | — |

### Relative mix levels (for a −14 LUFS master)
| Element | Guideline |
|---------|-----------|
| Dialogue | The anchor; around −14 to −16 LUFS short-term |
| Music under dialogue | 15–25 dB below dialogue (peaks around −28 to −22 dBFS) |
| Music with no dialogue | Bring up near dialogue level |
| SFX | Supports, doesn't mask speech |
| Room tone | Fill every dialogue gap so silence never drops to digital zero |

**Ducking:** Fairlight → music track Dynamics → Compressor with sidechain key = dialogue bus, ratio 3:1–5:1, 6–10 dB reduction; or in Resolve 19+, use automatic ducking in the Inspector/Fairlight where available.

**Fairlight loudness meter:** Fairlight page → Meters → Loudness → set the standard in Project Settings → Fairlight → Loudness.

---

## 6. Audio APIs (what the agent CAN script)

```python
# Voice Isolation on a clip (Studio)
item.SetVoiceIsolationState({"isEnabled": True, "amount": 70})
item.GetVoiceIsolationState()                 # -> {"isEnabled": True, "amount": 70}

# Voice Isolation on an entire audio track (Studio)
timeline.SetVoiceIsolationState(1, {"isEnabled": True, "amount": 60})

# Add tracks
timeline.AddTrack("audio", "stereo")          # mono, stereo, 5.1, 7.1, adaptive1..36 …
timeline.AddTrack("audio", {"audioType": "mono", "index": 2})
timeline.SetTrackName("audio", 1, "DIALOGUE")
timeline.SetTrackEnable("audio", 3, False)    # mute-equivalent: disable track
timeline.SetTrackLock("audio", 2, True)

# Sync external audio to camera clips
mediaPool.AutoSyncAudio([videoItem, audioItem], {
    resolve.AUDIO_SYNC_MODE: resolve.AUDIO_SYNC_WAVEFORM,   # or AUDIO_SYNC_TIMECODE
    resolve.AUDIO_SYNC_CHANNEL_NUMBER: resolve.AUDIO_SYNC_CHANNEL_AUTOMATIC,
    resolve.AUDIO_SYNC_RETAIN_EMBEDDED_AUDIO: False,
})

# Transcription & classification (Studio)
mpItem.TranscribeAudio(True)                  # True = speaker detection
folder.TranscribeAudio()                      # whole bin
mpItem.PerformAudioClassification()           # dialogue / music / effects categories

# AI text-to-speech (Studio + "AI Speech Generator" from Extras Download Manager)
project.GenerateSpeech({
    "TextInput": "Welcome back to the channel!",   # max 350 chars
    "VoiceModel": "Female 1",
    "Speed": 0, "Pitch": 0, "Variation": 0,
    "Filename": "vo_intro",
    "AddToTimeline": True, "AudioTrack": 2,
}, "01:00:00:00")

# Insert audio at the playhead on the selected Fairlight track
project.InsertAudioToCurrentTrackAtPlayhead("/sfx/whoosh.wav", 0, 48000)  # offset & duration in samples

# Fairlight presets (created in the UI's Fairlight preset library). The API docs don't say
# exactly what a preset stores, so test once that yours restores the FX/EQ/dynamics you expect.
resolve.GetFairlightPresets()
project.ApplyFairlightPresetToCurrentTimeline("Podcast Voice Chain")

# Audio-only render
project.SetRenderSettings({"ExportVideo": False, "ExportAudio": True,
                           "AudioCodec": "aac", "AudioSampleRate": 48000, "AudioBitDepth": 24})

# Inspect channel mapping
item.GetSourceAudioChannelMapping()           # JSON string
```

### External pre-processing (W5) — loudness/EQ/compression with ffmpeg
```bash
# Two-pass-accurate loudness normalization is better; this single-pass version is fine for drafts
ffmpeg -i dialog.wav -af "highpass=f=90,equalizer=f=300:t=q:w=1.2:g=-3,equalizer=f=4000:t=q:w=1:g=2,acompressor=threshold=-20dB:ratio=3:attack=15:release=150:makeup=2,loudnorm=I=-16:TP=-1.5:LRA=11" -ar 48000 dialog_proc.wav
```
Then `mpItem.ReplaceClip("/path/dialog_proc.wav")` to swap the source without touching the edit.

---

## 7. Audio Problem → Fix Lookup

| Problem | First fix | Second fix |
|---------|-----------|------------|
| Constant hiss / fan noise | Noise Reduction (Learn) | Voice Isolation 40–60 ⭐ |
| Background chatter / music under speech | Voice Isolation 70–90 ⭐ | Dialogue Separator ⭐ |
| 50/60 Hz hum | De-Hummer | Notch EQ at 50/60 Hz + harmonics |
| Boomy / muddy voice | HPF 90 Hz + cut 250–400 Hz | Multiband compressor (low band) |
| Harsh S sounds | De-Esser 6–7 kHz | Narrow EQ cut |
| Volume jumps between sentences | Dialogue Leveler ⭐ | Compressor 3:1 + manual clip gain |
| Clicks at cuts | 2–5 frame fades | Cross Fade 0 dB |
| Echoey room | Voice Isolation ⭐ (reduces reverb) | Dialogue Separator ⭐ (reduce Ambience) |
| Plosives (P/B pops) | Dialogue Processor → De-Pop | HPF 100 Hz + clip-gain dip |
| Music too loud vs. voice | Lower music 15–25 dB under dialogue | Sidechain ducking |
| Clipped/distorted recording | Soft Clipper (masks it slightly) | Re-record; clipping is mostly unrecoverable |
| Out-of-sync audio | `AutoSyncAudio` (waveform) | Slip the clip manually |
| Mono mic recorded on one channel only | Clip Attributes → Audio → map to mono/both channels | Stereo Fixer |

## 8. UI Click Paths

- **Clip volume:** Edit page → select the clip → Inspector → Audio → Volume. Or drag the volume line on the clip.
- **Add a Fairlight FX to a clip:** Effects → Audio FX → drag onto the audio clip → click the FX icon on the clip to open the plugin.
- **Add a Fairlight FX to a track:** Fairlight page → Mixer → Effects slot (+) → choose the plugin.
- **Normalize:** select clips → right-click → **Normalize Audio Levels** → Mode: ITU-R BS.1770-4 → Target −14 LUFS → Independent.
- **Dialogue Leveler / Voice Isolation:** Inspector → Audio → toggle on → adjust.
- **Save the track chain as a preset:** Fairlight page → mixer effects/EQ/dynamics → preset menu → Save. Then the agent applies it via the API.
