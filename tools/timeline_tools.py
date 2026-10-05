from typing import Any, Dict, List, Optional, Union
from resolve_bridge import bridge

def list_timelines() -> Dict[str, Any]:
    """List all timelines in the current project."""
    project = bridge.get_current_project()
    count = project.GetTimelineCount()
    timelines = []
    current = project.GetCurrentTimeline()
    current_name = current.GetName() if current else None

    for i in range(1, count + 1):
        tl = project.GetTimelineByIndex(i)
        if tl:
            timelines.append({
                "index": i,
                "name": tl.GetName(),
                "is_current": (tl.GetName() == current_name)
            })

    return {
        "count": len(timelines),
        "current_timeline": current_name,
        "timelines": timelines
    }

def set_current_timeline(timeline_name_or_index: Union[str, int]) -> Dict[str, Any]:
    """Switch active timeline by name or 1-based index."""
    project = bridge.get_current_project()
    count = project.GetTimelineCount()
    target_tl = None

    if isinstance(timeline_name_or_index, int) or str(timeline_name_or_index).isdigit():
        idx = int(timeline_name_or_index)
        if 1 <= idx <= count:
            target_tl = project.GetTimelineByIndex(idx)
    else:
        for i in range(1, count + 1):
            tl = project.GetTimelineByIndex(i)
            if tl and tl.GetName() == timeline_name_or_index:
                target_tl = tl
                break

    if not target_tl:
        return {"success": False, "error": f"Timeline '{timeline_name_or_index}' not found."}

    success = project.SetCurrentTimeline(target_tl)
    return {"success": bool(success), "active_timeline": target_tl.GetName()}

def duplicate_timeline(new_name: str) -> Dict[str, Any]:
    """Duplicate the current active timeline for safe non-destructive edits."""
    timeline = bridge.get_current_timeline()
    new_tl = timeline.DuplicateTimeline(new_name)
    if not new_tl:
        return {"success": False, "error": f"Failed to duplicate timeline to '{new_name}'."}
    return {"success": True, "duplicated_timeline": new_tl.GetName()}

def get_timeline_info() -> Dict[str, Any]:
    """Get metadata for active timeline: tracks, start/end frame, start timecode."""
    timeline = bridge.get_current_timeline()
    video_tracks = timeline.GetTrackCount("video")
    audio_tracks = timeline.GetTrackCount("audio")
    subtitle_tracks = timeline.GetTrackCount("subtitle")

    return {
        "name": timeline.GetName(),
        "start_frame": timeline.GetStartFrame(),
        "end_frame": timeline.GetEndFrame(),
        "start_timecode": timeline.GetStartTimecode(),
        "track_counts": {
            "video": video_tracks,
            "audio": audio_tracks,
            "subtitle": subtitle_tracks
        }
    }

def get_track_items(track_type: str = "video", track_index: int = 1) -> Dict[str, Any]:
    """List all clips (TimelineItems) in a given track with timing and clip names."""
    timeline = bridge.get_current_timeline()
    valid_types = {"video", "audio", "subtitle"}
    if track_type.lower() not in valid_types:
        return {"success": False, "error": f"Invalid track_type '{track_type}'. Must be one of: {valid_types}"}

    items = timeline.GetItemListInTrack(track_type.lower(), track_index) or []
    item_list = []
    for idx, item in enumerate(items, start=1):
        mp_item = item.GetMediaPoolItem()
        item_list.append({
            "index": idx,
            "name": item.GetName(),
            "start": item.GetStart(),
            "end": item.GetEnd(),
            "duration": item.GetDuration(),
            "source_clip": mp_item.GetName() if mp_item else None
        })

    return {
        "success": True,
        "track_type": track_type.lower(),
        "track_index": track_index,
        "item_count": len(item_list),
        "items": item_list
    }

def get_clip_properties(track_type: str = "video", track_index: int = 1, item_index: int = 1, property_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Get clip Inspector properties (Pan, Tilt, ZoomX, ZoomY, Crop, CompositeMode, etc.).
    Returns all properties if property_key is omitted.
    """
    timeline = bridge.get_current_timeline()
    items = timeline.GetItemListInTrack(track_type.lower(), track_index) or []
    if not (1 <= item_index <= len(items)):
        return {"success": False, "error": f"Item index {item_index} out of range (1..{len(items)})."}

    item = items[item_index - 1]
    if property_key:
        val = item.GetProperty(property_key)
        return {"success": True, "property": property_key, "value": val}
    else:
        props = item.GetProperty()
        return {"success": True, "properties": props}

def set_clip_properties(track_type: str = "video", track_index: int = 1, item_index: int = 1, properties: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Set Inspector properties for a clip.
    Supported keys include:
    - Transform: Pan, Tilt, ZoomX, ZoomY, ZoomGang, RotationAngle, AnchorPointX, AnchorPointY, Pitch, Yaw, FlipX, FlipY
    - Cropping: CropLeft, CropRight, CropTop, CropBottom, CropSoftness, CropRetain
    - Composite: CompositeMode (0=Normal, 1=Add, 2=Subtract, 3=Diff, 4=Multiply, 5=Screen, 6=Overlay...), Opacity
    """
    if not properties:
        return {"success": False, "error": "No properties dictionary provided."}

    timeline = bridge.get_current_timeline()
    items = timeline.GetItemListInTrack(track_type.lower(), track_index) or []
    if not (1 <= item_index <= len(items)):
        return {"success": False, "error": f"Item index {item_index} out of range (1..{len(items)})."}

    item = items[item_index - 1]
    results = {}
    for k, v in properties.items():
        ok = item.SetProperty(k, v)
        results[k] = bool(ok)

    return {
        "success": all(results.values()),
        "clip_name": item.GetName(),
        "applied_properties": results
    }

def add_marker(frame_id: int, color: str = "Blue", name: str = "", note: str = "", duration: int = 1) -> Dict[str, Any]:
    """
    Add a marker to the current timeline at a specific frame index.
    Colors: Blue, Cyan, Green, Yellow, Red, Pink, Purple, Fuchsia, Rose, Lavender, Sky, Mint, Lemon, Sand, Cocoa, Cream.
    """
    timeline = bridge.get_current_timeline()
    ok = timeline.AddMarker(frame_id, color, name, note, duration, "")
    return {"success": bool(ok), "frame_id": frame_id, "color": color, "name": name}

def get_markers() -> Dict[str, Any]:
    """Get all markers from the current timeline."""
    timeline = bridge.get_current_timeline()
    markers = timeline.GetMarkers() or {}
    return {
        "success": True,
        "marker_count": len(markers),
        "markers": markers
    }

def delete_marker(frame_id: Optional[int] = None, color: Optional[str] = None) -> Dict[str, Any]:
    """Delete a marker at frame_id, or delete all markers of a specific color."""
    timeline = bridge.get_current_timeline()
    if frame_id is not None:
        ok = timeline.DeleteMarkerAtFrame(frame_id)
        return {"success": bool(ok), "deleted_frame": frame_id}
    elif color:
        ok = timeline.DeleteMarkersByColor(color)
        return {"success": bool(ok), "deleted_color": color}
    return {"success": False, "error": "Specify either frame_id or color."}
