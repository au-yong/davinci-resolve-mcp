from typing import Any, Dict, List, Optional
from resolve_bridge import bridge

def _find_folder(folder: Any, name: str) -> Optional[Any]:
    """Helper to recursively find a Media Pool subfolder by name."""
    if folder.GetName() == name:
        return folder
    sub_folders = folder.GetSubFolderList() or []
    for sub in sub_folders:
        found = _find_folder(sub, name)
        if found:
            return found
    return None

def get_media_pool_structure() -> Dict[str, Any]:
    """Inspect the Media Pool folder hierarchy and clip counts."""
    mp = bridge.get_media_pool()
    root = mp.GetRootFolder()

    def serialize_folder(f: Any) -> Dict[str, Any]:
        clips = f.GetClipList() or []
        subs = f.GetSubFolderList() or []
        return {
            "name": f.GetName(),
            "clip_count": len(clips),
            "subfolders": [serialize_folder(s) for s in subs]
        }

    return serialize_folder(root)

def create_bin(bin_name: str, parent_bin_name: Optional[str] = None) -> Dict[str, Any]:
    """Create a new bin (folder) in the Media Pool."""
    mp = bridge.get_media_pool()
    root = mp.GetRootFolder()
    parent = root
    if parent_bin_name:
        parent = _find_folder(root, parent_bin_name)
        if not parent:
            return {"success": False, "error": f"Parent bin '{parent_bin_name}' not found."}

    new_folder = mp.AddSubFolder(parent, bin_name)
    if not new_folder:
        return {"success": False, "error": f"Failed to create bin '{bin_name}'."}
    return {"success": True, "bin_name": new_folder.GetName()}

def import_media(file_paths: List[str], target_bin_name: Optional[str] = None) -> Dict[str, Any]:
    """Import audio, video, or image files into the Media Pool."""
    mp = bridge.get_media_pool()
    if target_bin_name:
        root = mp.GetRootFolder()
        target = _find_folder(root, target_bin_name)
        if target:
            mp.SetCurrentFolder(target)
        else:
            return {"success": False, "error": f"Target bin '{target_bin_name}' not found."}

    items = mp.ImportMedia(file_paths)
    if not items:
        return {"success": False, "imported_count": 0, "error": "Import returned no items. Verify file paths exist and are supported."}

    imported_names = [item.GetName() for item in items if item]
    return {
        "success": True,
        "imported_count": len(imported_names),
        "items": imported_names
    }

def list_media_pool_clips(bin_name: Optional[str] = None) -> Dict[str, Any]:
    """List clips in a specified Media Pool bin or the root folder."""
    mp = bridge.get_media_pool()
    root = mp.GetRootFolder()
    target_folder = root
    if bin_name:
        target_folder = _find_folder(root, bin_name)
        if not target_folder:
            return {"success": False, "error": f"Bin '{bin_name}' not found."}

    clips = target_folder.GetClipList() or []
    clip_details = []
    for c in clips:
        props = c.GetClipProperty() or {}
        clip_details.append({
            "name": c.GetName(),
            "duration": props.get("Duration"),
            "fps": props.get("FPS"),
            "resolution": props.get("Resolution"),
            "format": props.get("Format"),
            "type": props.get("Type")
        })

    return {
        "success": True,
        "bin": target_folder.GetName(),
        "count": len(clip_details),
        "clips": clip_details
    }

def create_empty_timeline(timeline_name: str) -> Dict[str, Any]:
    """Create a new empty timeline in the active project."""
    mp = bridge.get_media_pool()
    timeline = mp.CreateEmptyTimeline(timeline_name)
    if not timeline:
        return {"success": False, "error": f"Failed to create empty timeline '{timeline_name}'."}
    project = bridge.get_current_project()
    project.SetCurrentTimeline(timeline)
    return {"success": True, "timeline_name": timeline.GetName()}

def create_timeline_from_clips(timeline_name: str, clip_names: List[str], bin_name: Optional[str] = None) -> Dict[str, Any]:
    """Create a new timeline populated with the specified clips from the Media Pool."""
    mp = bridge.get_media_pool()
    root = mp.GetRootFolder()
    search_folder = _find_folder(root, bin_name) if bin_name else root
    if not search_folder:
        search_folder = root

    available_clips = {c.GetName(): c for c in (search_folder.GetClipList() or [])}
    selected_items = [available_clips[name] for name in clip_names if name in available_clips]

    if not selected_items:
        return {"success": False, "error": "None of the specified clip names were found in the selected bin."}

    timeline = mp.CreateTimelineFromClips(timeline_name, selected_items)
    if not timeline:
        return {"success": False, "error": f"Failed to create timeline from clips for '{timeline_name}'."}

    project = bridge.get_current_project()
    project.SetCurrentTimeline(timeline)
    return {
        "success": True,
        "timeline_name": timeline.GetName(),
        "clips_added": len(selected_items)
    }

def append_clips_to_timeline(clip_names: List[str], track_index: int = 1, bin_name: Optional[str] = None) -> Dict[str, Any]:
    """Append specified clips from the Media Pool to the end of the currently active timeline."""
    mp = bridge.get_media_pool()
    root = mp.GetRootFolder()
    search_folder = _find_folder(root, bin_name) if bin_name else root
    if not search_folder:
        search_folder = root

    available_clips = {c.GetName(): c for c in (search_folder.GetClipList() or [])}
    items_to_append = []
    for name in clip_names:
        if name in available_clips:
            items_to_append.append({
                "mediaPoolItem": available_clips[name],
                "trackIndex": track_index
            })

    if not items_to_append:
        return {"success": False, "error": "None of the specified clips were found in the Media Pool."}

    result = mp.AppendToTimeline(items_to_append)
    return {
        "success": bool(result),
        "appended_count": len(result) if result else 0
    }
