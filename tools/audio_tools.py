from typing import Any, Dict, List, Optional
from resolve_bridge import bridge

def get_voice_isolation(track_type: str = "video", track_index: int = 1, item_index: int = 1) -> Dict[str, Any]:
    """
    Get the DaVinci Neural Engine Voice Isolation state for a timeline clip (Studio version).
    """
    try:
        timeline = bridge.get_current_timeline()
        items = timeline.GetItemListInTrack(track_type.lower(), track_index) or []
        if not (1 <= item_index <= len(items)):
            return {"success": False, "error": f"Item index {item_index} out of range (1..{len(items)})."}

        item = items[item_index - 1]
        if not hasattr(item, "GetVoiceIsolationState"):
            return {
                "success": False,
                "error": "Voice Isolation requires DaVinci Resolve Studio (not supported in Free edition)."
            }

        state = item.GetVoiceIsolationState()
        if state is None:
            return {
                "success": False,
                "error": "Voice Isolation state could not be read. This feature requires DaVinci Resolve Studio."
            }

        return {
            "success": True,
            "clip_name": item.GetName(),
            "voice_isolation": state
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Voice Isolation requires DaVinci Resolve Studio: {e}"
        }

def set_voice_isolation(
    track_type: str = "video",
    track_index: int = 1,
    item_index: int = 1,
    enabled: bool = True,
    amount: int = 65
) -> Dict[str, Any]:
    """
    Enable/disable and set DaVinci Neural Engine Voice Isolation amount (0-100) on a clip (Studio).
    Recommended: 50-80 for background noise/HVAC removal without artifacts.
    """
    try:
        timeline = bridge.get_current_timeline()
        items = timeline.GetItemListInTrack(track_type.lower(), track_index) or []
        if not (1 <= item_index <= len(items)):
            return {"success": False, "error": f"Item index {item_index} out of range (1..{len(items)})."}

        item = items[item_index - 1]
        if not hasattr(item, "SetVoiceIsolationState"):
            return {
                "success": False,
                "error": "Voice Isolation is a DaVinci Neural Engine feature that requires DaVinci Resolve Studio."
            }

        clamped_amount = max(0, min(100, int(amount)))
        state = {"isEnabled": bool(enabled), "amount": clamped_amount}
        ok = item.SetVoiceIsolationState(state)
        if not ok:
            return {
                "success": False,
                "error": "SetVoiceIsolationState returned False. This feature requires DaVinci Resolve Studio."
            }

        return {
            "success": True,
            "clip_name": item.GetName(),
            "voice_isolation": state
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Voice Isolation requires DaVinci Resolve Studio: {e}"
        }

def create_subtitles_from_audio(
    language: Optional[str] = None,
    max_characters_per_line: int = 42,
    lines: str = "Double"
) -> Dict[str, Any]:
    """
    Trigger DaVinci Resolve Studio automatic speech-to-text subtitle generation.
    lines: 'Single' or 'Double'
    """
    try:
        timeline = bridge.get_current_timeline()
        if not hasattr(timeline, "CreateSubtitlesFromAudio"):
            return {
                "success": False,
                "error": "Speech-to-text auto subtitles requires DaVinci Resolve Studio."
            }

        settings = {
            "maxCharactersPerLine": int(max_characters_per_line),
            "lines": lines
        }
        if language:
            settings["language"] = language

        ok = timeline.CreateSubtitlesFromAudio(settings)
        if not ok:
            return {
                "success": False,
                "error": (
                    "CreateSubtitlesFromAudio returned False. Ensure you are running DaVinci Resolve Studio "
                    "and have installed language models via DaVinci Resolve > Extras Download Manager."
                )
            }

        return {
            "success": True,
            "settings": settings,
            "note": "Requires DaVinci Resolve Studio with speech-to-text models installed."
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Speech-to-text auto subtitles requires DaVinci Resolve Studio: {e}"
        }

def get_fairlight_presets() -> Dict[str, Any]:
    """Get list of saved Fairlight presets in Resolve."""
    resolve = bridge.get_resolve()
    presets = resolve.GetFairlightPresets() or []
    return {
        "success": True,
        "presets": presets
    }

def apply_fairlight_preset(preset_name: str) -> Dict[str, Any]:
    """Apply a saved Fairlight audio preset to the active timeline."""
    project = bridge.get_current_project()
    ok = project.ApplyFairlightPresetToCurrentTimeline(preset_name)
    return {
        "success": bool(ok),
        "preset_name": preset_name
    }
