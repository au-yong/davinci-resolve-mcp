# DaVinci Resolve Knowledge Base for AI Agents

A reference that teaches an AI agent (Claude) how to **plan, apply, and automate** effects, audio processing, graphics, and adjustments in DaVinci Resolve, through the scripting API, an MCP server, or step-by-step UI guidance.

> Verified against the DaVinci Resolve Scripting API README **v21.0.4** (July 2026). Method names in these files come from that reference. Effect names come from the Resolve Effects Library and may vary slightly between versions.

---

## Files

| # | File | What it covers |
|---|------|----------------|
| 00 | [00-capability-matrix.md](00-capability-matrix.md) | **Read first.** What the agent can do directly via API, what needs a workaround, and what is UI-only |
| 01 | [01-video-effects-resolvefx.md](01-video-effects-resolvefx.md) | Resolve FX / OpenFX catalog by category, with purpose, key parameters, and typical values |
| 02 | [02-transitions.md](02-transitions.md) | Video and audio transitions, plus how to automate them |
| 03 | [03-titles-graphics-generators.md](03-titles-graphics-generators.md) | Titles, Text+, Fusion titles, generators, subtitles, and the `Insert*IntoTimeline` APIs |
| 04 | [04-fusion-scripting.md](04-fusion-scripting.md) | Fusion tool IDs, inputs, node wiring, keyframes, and graphics recipes in code |
| 05 | [05-audio-fairlight.md](05-audio-fairlight.md) | Fairlight FX catalog, mixer, EQ/dynamics cheat sheet, loudness targets, audio APIs |
| 06 | [06-color-grading.md](06-color-grading.md) | Color page tools, node workflow, CDL/LUT/DRX automation, look recipes |
| 07 | [07-inspector-properties.md](07-inspector-properties.md) | Exact `TimelineItem.SetProperty` keys, ranges, and enum values |
| 08 | [08-recipes.md](08-recipes.md) | End-to-end agent workflows (YouTube, podcast, social vertical, and more) |

---

## Golden Rules for the Agent

1. **Check the version and edition first.** Call `resolve.GetVersionString()` and `resolve.GetProductName()`. Many AI features and all external scripting need **DaVinci Resolve Studio**.
2. **Know the API boundary.** The scripting API **cannot** drag a Resolve FX, transition, or Fairlight FX onto a clip. Use the workarounds in [00-capability-matrix.md](00-capability-matrix.md): DRX grades, Fusion comps, Fusion templates, timeline interchange (FCPXML/OTIO), or UI guidance.
3. **Indexes are 1-based.** Tracks, node indexes, Fusion comp indexes, and take indexes all start at 1.
4. **Check every return value.** Most setters return `True`/`False`. Insert functions return `None` when a name doesn't match. Never assume success.
5. **Save before destructive operations.** Call `projectManager.SaveProject()` before bulk edits, and duplicate the timeline (`timeline.DuplicateTimeline("v2")`) before large automated changes.
6. **Discover instead of guessing.** `item.GetProperty()` with no arguments returns all supported keys. In Fusion, `tool.GetInputList()` and `comp.GetToolList()` reveal real input names.
7. **Prefer non-destructive edits.** Use color versions (`AddVersion`), duplicated timelines, and Fusion comps rather than overwriting.
8. **Be honest with the user.** If something is UI-only, give exact click paths rather than claiming you applied it.

---

## Ways to Load This Into Claude

| Method | How |
|--------|-----|
| **Claude Projects** | Upload all `.md` files as Project Knowledge |
| **Claude Code / agent repo** | Put this folder in the repo and reference it from `CLAUDE.md` (e.g. "Before any Resolve task, read `davinci-resolve-kb/00-capability-matrix.md`") |
| **MCP server resources** | Expose each file as an MCP `resource` (e.g. `resolve-kb://audio`) so the agent loads only what it needs |
| **MCP prompt** | Expose [08-recipes.md](08-recipes.md) workflows as MCP `prompts` |

---

## Glossary

| Term | Meaning |
|------|---------|
| **Resolve FX / OpenFX (OFX)** | Built-in GPU video effects (Glow, Blur, Film Grain…) plus third-party OFX plugins |
| **Fairlight FX** | Built-in audio plugins (EQ, De-Esser, Reverb…) |
| **Fusion** | Node-based compositing and motion graphics engine inside Resolve |
| **Text+** | Fusion-powered title tool, more flexible than the basic Text title |
| **DRX** | Saved DaVinci grade file (a still plus its node tree, which can contain Resolve FX) |
| **PowerGrade** | Gallery album of grades that persists across projects |
| **CDL** | Color Decision List: Slope, Offset, Power, Saturation |
| **LUFS** | Loudness Units relative to Full Scale, the standard measure of perceived loudness |
| **DNE** | DaVinci Neural Engine (the AI features) |
