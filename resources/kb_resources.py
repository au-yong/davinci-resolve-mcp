import os
from pathlib import Path
from typing import Dict

KB_DIR = Path(__file__).parent.parent / "davinci-resolve-kb"

def read_kb_file(filename: str) -> str:
    """Read a markdown file from the davinci-resolve-kb folder."""
    target = KB_DIR / filename
    if target.exists():
        return target.read_text(encoding="utf-8")
    return f"Knowledge base file '{filename}' not found."

KB_RESOURCES = {
    "capabilities": ("resolve-kb://capabilities", "00-capability-matrix.md", "Direct API vs Workarounds vs UI-only capabilities matrix"),
    "effects": ("resolve-kb://effects", "01-video-effects-resolvefx.md", "Resolve FX & OpenFX parameters catalog"),
    "transitions": ("resolve-kb://transitions", "02-transitions.md", "Video and audio transitions guide"),
    "graphics": ("resolve-kb://graphics", "03-titles-graphics-generators.md", "Titles, generators, Text+, and subtitle automation"),
    "fusion": ("resolve-kb://fusion", "04-fusion-scripting.md", "Fusion node wiring, tool IDs, and keyframing in code"),
    "audio": ("resolve-kb://audio", "05-audio-fairlight.md", "Fairlight audio FX, EQ, LUFS loudness, and voice isolation"),
    "color": ("resolve-kb://color", "06-color-grading.md", "Color grading, node trees, CDL, LUTs, and DRX grades"),
    "inspector": ("resolve-kb://inspector", "07-inspector-properties.md", "TimelineItem.SetProperty keys and ranges"),
    "recipes": ("resolve-kb://recipes", "08-recipes.md", "End-to-end recipes for YouTube, Podcasts, Social Reels"),
    "readme": ("resolve-kb://readme", "README.md", "Knowledge base index, golden rules, and architecture"),
    "api_reference": ("resolve-kb://api-reference", "api_ref.txt", "Raw DaVinci Resolve Scripting API reference extract"),
}
