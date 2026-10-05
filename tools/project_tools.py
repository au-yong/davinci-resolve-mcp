from typing import Any, Dict, List, Optional
from resolve_bridge import bridge

def get_resolve_status() -> Dict[str, Any]:
    """Check connection to DaVinci Resolve and return current software and project state."""
    return bridge.get_status()

def list_projects() -> Dict[str, Any]:
    """List all project names in the current database / project manager folder."""
    pm = bridge.get_project_manager()
    project_list = pm.GetProjectListInCurrentFolder()
    return {
        "count": len(project_list) if project_list else 0,
        "projects": project_list or []
    }

def open_project(project_name: str) -> Dict[str, Any]:
    """Load an existing project by name in DaVinci Resolve."""
    pm = bridge.get_project_manager()
    proj = pm.LoadProject(project_name)
    if not proj:
        return {"success": False, "error": f"Failed to load project '{project_name}'. Verify the project exists."}
    return {
        "success": True,
        "project_name": proj.GetName(),
        "timeline_count": proj.GetTimelineCount()
    }

def create_project(project_name: str) -> Dict[str, Any]:
    """Create a new project and open it in DaVinci Resolve."""
    pm = bridge.get_project_manager()
    proj = pm.CreateProject(project_name)
    if not proj:
        return {"success": False, "error": f"Failed to create project '{project_name}'. A project with this name may already exist."}
    return {
        "success": True,
        "project_name": proj.GetName()
    }

def save_project() -> Dict[str, Any]:
    """Save the currently open project."""
    pm = bridge.get_project_manager()
    success = pm.SaveProject()
    return {"success": bool(success)}

def close_project() -> Dict[str, Any]:
    """Close the currently open project and return to Project Manager."""
    pm = bridge.get_project_manager()
    current_proj = pm.GetCurrentProject()
    if not current_proj:
        return {"success": False, "error": "No project is currently open."}
    name = current_proj.GetName()
    success = pm.CloseProject(current_proj)
    return {"success": bool(success), "closed_project": name}

def get_project_settings(keys: Optional[List[str]] = None) -> Dict[str, Any]:
    """Get project configuration settings (e.g., timelineResolutionWidth, timelineResolutionHeight, timelineFrameRate)."""
    proj = bridge.get_current_project()
    all_settings = proj.GetSetting()
    if not keys:
        # Return common standard settings if none specified
        common_keys = [
            "timelineResolutionWidth", "timelineResolutionHeight",
            "timelineFrameRate", "timelinePlaybackFrameRate",
            "videoMonitorFormat", "colorScienceMode"
        ]
        return {k: all_settings.get(k) for k in common_keys if k in all_settings}
    return {k: all_settings.get(k) for k in keys if k in all_settings}

def set_project_setting(setting_name: str, value: str) -> Dict[str, Any]:
    """Set a project configuration setting (e.g. 'timelineResolutionWidth', '1080')."""
    proj = bridge.get_current_project()
    success = proj.SetSetting(setting_name, str(value))
    return {
        "success": bool(success),
        "setting": setting_name,
        "value": value
    }
