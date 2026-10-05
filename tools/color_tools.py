from typing import Any, Dict, List, Optional
from resolve_bridge import bridge

def apply_grade_from_drx(
    drx_path: str,
    grade_mode: int = 0,
    track_index: int = 1,
    item_index: int = 1
) -> Dict[str, Any]:
    """
    Apply a saved .drx grade file (PowerGrade / Still) to a timeline clip.
    grade_mode: 0 = No keyframes, 1 = Source Timecode aligned, 2 = Start Frames aligned.
    """
    timeline = bridge.get_current_timeline()
    items = timeline.GetItemListInTrack("video", track_index) or []
    if not (1 <= item_index <= len(items)):
        return {"success": False, "error": f"Item index {item_index} out of range on video track {track_index}."}

    item = items[item_index - 1]
    ok = item.ApplyGradeFromDRX(drx_path, grade_mode)
    return {
        "success": bool(ok),
        "clip_name": item.GetName(),
        "drx_path": drx_path,
        "grade_mode": grade_mode
    }

def set_clip_cdl(
    track_index: int = 1,
    item_index: int = 1,
    node_index: int = 1,
    slope: Optional[List[float]] = None,
    offset: Optional[List[float]] = None,
    power: Optional[List[float]] = None,
    saturation: Optional[float] = None
) -> Dict[str, Any]:
    """
    Apply CDL (Color Decision List) values to a specific node on a timeline clip.
    node_index is 1-based.
    slope: [r, g, b] (default [1.0, 1.0, 1.0])
    offset: [r, g, b] (default [0.0, 0.0, 0.0])
    power: [r, g, b] (default [1.0, 1.0, 1.0])
    saturation: float (default 1.0)
    """
    timeline = bridge.get_current_timeline()
    items = timeline.GetItemListInTrack("video", track_index) or []
    if not (1 <= item_index <= len(items)):
        return {"success": False, "error": f"Item index {item_index} out of range on video track {track_index}."}

    item = items[item_index - 1]
    cdl_map = {}
    if slope and len(slope) == 3:
        cdl_map["Slope"] = f"{slope[0]} {slope[1]} {slope[2]}"
    if offset and len(offset) == 3:
        cdl_map["Offset"] = f"{offset[0]} {offset[1]} {offset[2]}"
    if power and len(power) == 3:
        cdl_map["Power"] = f"{power[0]} {power[1]} {power[2]}"
    if saturation is not None:
        cdl_map["Saturation"] = str(saturation)

    if not cdl_map:
        return {"success": False, "error": "No CDL parameters provided."}

    try:
        ok = item.SetCDL(node_index, cdl_map)
    except TypeError:
        # Some versions accept a single dict with NodeIndex key
        cdl_map["NodeIndex"] = str(node_index)
        ok = item.SetCDL(cdl_map)

    return {
        "success": bool(ok),
        "clip_name": item.GetName(),
        "node_index": node_index,
        "cdl_applied": cdl_map
    }

def set_clip_lut(
    track_index: int = 1,
    item_index: int = 1,
    node_index: int = 1,
    lut_path: str = ""
) -> Dict[str, Any]:
    """
    Apply a 3D LUT (.cube file) to a color node on a clip.
    node_index is 1-based.
    """
    timeline = bridge.get_current_timeline()
    items = timeline.GetItemListInTrack("video", track_index) or []
    if not (1 <= item_index <= len(items)):
        return {"success": False, "error": f"Item index {item_index} out of range on video track {track_index}."}

    item = items[item_index - 1]
    ok = item.SetLUT(node_index, lut_path)
    return {
        "success": bool(ok),
        "clip_name": item.GetName(),
        "node_index": node_index,
        "lut_path": lut_path
    }

def add_color_version(
    track_index: int = 1,
    item_index: int = 1,
    version_name: str = "Version 2",
    version_type: int = 0
) -> Dict[str, Any]:
    """
    Create a new color version for non-destructive grade comparisons.
    version_type: 0 = Local version, 1 = Remote version.
    """
    timeline = bridge.get_current_timeline()
    items = timeline.GetItemListInTrack("video", track_index) or []
    if not (1 <= item_index <= len(items)):
        return {"success": False, "error": f"Item index {item_index} out of range on video track {track_index}."}

    item = items[item_index - 1]
    ok = item.AddVersion(version_name, version_type)
    return {
        "success": bool(ok),
        "clip_name": item.GetName(),
        "version_name": version_name
    }

def list_color_versions(
    track_index: int = 1,
    item_index: int = 1,
    version_type: int = 0
) -> Dict[str, Any]:
    """List available color versions on a clip."""
    timeline = bridge.get_current_timeline()
    items = timeline.GetItemListInTrack("video", track_index) or []
    if not (1 <= item_index <= len(items)):
        return {"success": False, "error": f"Item index {item_index} out of range on video track {track_index}."}

    item = items[item_index - 1]
    versions = item.GetVersionNameList(version_type) or []
    current = item.GetCurrentVersion(version_type)
    return {
        "success": True,
        "clip_name": item.GetName(),
        "current_version": current,
        "versions": versions
    }
