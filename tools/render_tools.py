from typing import Any, Dict, List, Optional
from resolve_bridge import bridge

def get_render_presets() -> Dict[str, Any]:
    """Get list of available render presets (e.g. YouTube, ProRes, H.264, Vimeo)."""
    project = bridge.get_current_project()
    presets = project.GetRenderPresetList() or []
    return {
        "success": True,
        "count": len(presets),
        "presets": presets
    }

def load_render_preset(preset_name: str) -> Dict[str, Any]:
    """Load a render preset into the active export configuration."""
    project = bridge.get_current_project()
    ok = project.LoadRenderPreset(preset_name)
    return {
        "success": bool(ok),
        "preset_name": preset_name
    }

def set_render_settings(
    target_dir: str,
    custom_name: str,
    format_name: Optional[str] = None,
    codec_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Configure export destination and file naming.
    target_dir: Absolute folder path for output file.
    custom_name: Base filename (without extension).
    format_name: Optional container format (e.g. 'mov', 'mp4').
    codec_name: Optional video codec (e.g. 'H264', 'H265', 'ProRes').
    """
    project = bridge.get_current_project()
    settings: Dict[str, Any] = {
        "TargetDir": target_dir,
        "CustomName": custom_name
    }
    if format_name:
        settings["FormatExtension"] = format_name
    if codec_name:
        settings["Codec"] = codec_name

    ok = project.SetRenderSettings(settings)
    return {
        "success": bool(ok),
        "settings_applied": settings
    }

def add_render_job() -> Dict[str, Any]:
    """Add the configured render setup to the Deliver page Render Queue."""
    project = bridge.get_current_project()
    job_id = project.AddRenderJob()
    if not job_id:
        return {"success": False, "error": "Failed to add job to render queue."}
    return {
        "success": True,
        "job_id": job_id
    }

def list_render_jobs() -> Dict[str, Any]:
    """List all jobs currently in the render queue."""
    project = bridge.get_current_project()
    jobs = project.GetRenderJobList() or []
    return {
        "success": True,
        "job_count": len(jobs),
        "jobs": jobs
    }

def start_rendering(job_ids: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Start rendering the queue.
    If job_ids is provided, renders only those jobs; otherwise renders all queued jobs.
    """
    project = bridge.get_current_project()
    if job_ids:
        ok = project.StartRendering(job_ids)
    else:
        ok = project.StartRendering()
    return {
        "success": bool(ok),
        "started_jobs": job_ids or "all"
    }

def get_render_status() -> Dict[str, Any]:
    """Check if rendering is currently in progress and get status of all jobs."""
    project = bridge.get_current_project()
    in_progress = project.IsRenderingInProgress()
    jobs = project.GetRenderJobList() or []
    job_statuses = []
    for j in jobs:
        jid = j.get("JobId")
        if jid:
            st = project.GetRenderJobStatus(jid)
            job_statuses.append({
                "job_id": jid,
                "status": st
            })

    return {
        "is_rendering": bool(in_progress),
        "jobs": job_statuses
    }

def stop_rendering() -> Dict[str, Any]:
    """Cancel / stop active rendering."""
    project = bridge.get_current_project()
    project.StopRendering()
    return {"success": True, "message": "Stop render signal sent."}

def delete_all_render_jobs() -> Dict[str, Any]:
    """Clear all jobs from the render queue."""
    project = bridge.get_current_project()
    ok = project.DeleteAllRenderJobs()
    return {"success": bool(ok)}
