import os
import sys
from typing import Any, Dict, List, Optional, Union
from dotenv import load_dotenv

load_dotenv()

# Compatibility shim for MCP SDK 2.x and 1.x
try:
    from mcp.server.mcpserver import MCPServer
    server = MCPServer("DaVinciResolveMCP")
except ImportError:
    from mcp.server.fastmcp import FastMCP
    server = FastMCP("DaVinciResolveMCP")

# Import tool implementations
from tools import project_tools
from tools import media_pool_tools
from tools import timeline_tools
from tools import fusion_graphics_tools
from tools import audio_tools
from tools import color_tools
from tools import render_tools
from resources.kb_resources import KB_RESOURCES, read_kb_file

# ==========================================
# 1. Project Management Tools
# ==========================================

@server.tool()
def get_resolve_status() -> Dict[str, Any]:
    """Check DaVinci Resolve connection status, product version, active project, and timeline."""
    return project_tools.get_resolve_status()

@server.tool()
def list_projects() -> Dict[str, Any]:
    """List all projects in the current DaVinci Resolve database / folder."""
    return project_tools.list_projects()

@server.tool()
def open_project(project_name: str) -> Dict[str, Any]:
    """Open an existing project by name in DaVinci Resolve."""
    return project_tools.open_project(project_name)

@server.tool()
def create_project(project_name: str) -> Dict[str, Any]:
    """Create a new project in DaVinci Resolve and switch to it."""
    return project_tools.create_project(project_name)

@server.tool()
def save_project() -> Dict[str, Any]:
    """Save the currently active project."""
    return project_tools.save_project()

@server.tool()
def close_project() -> Dict[str, Any]:
    """Close the current project and return to the Project Manager."""
    return project_tools.close_project()

@server.tool()
def get_project_settings(keys: Optional[List[str]] = None) -> Dict[str, Any]:
    """Get project configuration settings (resolution, framerate, color science)."""
    return project_tools.get_project_settings(keys)

@server.tool()
def set_project_setting(setting_name: str, value: str) -> Dict[str, Any]:
    """Set a project setting (e.g. 'timelineResolutionWidth', '1080')."""
    return project_tools.set_project_setting(setting_name, value)


# ==========================================
# 2. Media Pool Tools
# ==========================================

@server.tool()
def get_media_pool_structure() -> Dict[str, Any]:
    """Get the full hierarchy of bins (folders) and clip counts in the Media Pool."""
    return media_pool_tools.get_media_pool_structure()

@server.tool()
def create_bin(bin_name: str, parent_bin_name: Optional[str] = None) -> Dict[str, Any]:
    """Create a new bin (folder) in the Media Pool, optionally inside a parent bin."""
    return media_pool_tools.create_bin(bin_name, parent_bin_name)

@server.tool()
def import_media(file_paths: List[str], target_bin_name: Optional[str] = None) -> Dict[str, Any]:
    """Import media files (video, audio, images) into the Media Pool."""
    return media_pool_tools.import_media(file_paths, target_bin_name)

@server.tool()
def list_media_pool_clips(bin_name: Optional[str] = None) -> Dict[str, Any]:
    """List clips in a specified bin or root, with duration, FPS, and format info."""
    return media_pool_tools.list_media_pool_clips(bin_name)

@server.tool()
def create_empty_timeline(timeline_name: str) -> Dict[str, Any]:
    """Create a new empty timeline in the current project and set it active."""
    return media_pool_tools.create_empty_timeline(timeline_name)

@server.tool()
def create_timeline_from_clips(timeline_name: str, clip_names: List[str], bin_name: Optional[str] = None) -> Dict[str, Any]:
    """Create a new timeline populated with selected clips from the Media Pool."""
    return media_pool_tools.create_timeline_from_clips(timeline_name, clip_names, bin_name)

@server.tool()
def append_clips_to_timeline(clip_names: List[str], track_index: int = 1, bin_name: Optional[str] = None) -> Dict[str, Any]:
    """Append clips from the Media Pool to the end of the active timeline track."""
    return media_pool_tools.append_clips_to_timeline(clip_names, track_index, bin_name)


# ==========================================
# 3. Timeline Editing & Inspector Tools
# ==========================================

@server.tool()
def list_timelines() -> Dict[str, Any]:
    """List all timelines in the current project with their indices and names."""
    return timeline_tools.list_timelines()

@server.tool()
def set_current_timeline(timeline_name_or_index: Union[str, int]) -> Dict[str, Any]:
    """Switch the active timeline in DaVinci Resolve by name or 1-based index."""
    return timeline_tools.set_current_timeline(timeline_name_or_index)

@server.tool()
def duplicate_timeline(new_name: str) -> Dict[str, Any]:
    """Duplicate the active timeline to create a safe working copy before edits."""
    return timeline_tools.duplicate_timeline(new_name)

@server.tool()
def get_timeline_info() -> Dict[str, Any]:
    """Get current timeline start/end frames, timecode, and track counts."""
    return timeline_tools.get_timeline_info()

@server.tool()
def get_track_items(track_type: str = "video", track_index: int = 1) -> Dict[str, Any]:
    """List all clips/items in a track (video, audio, or subtitle) with in/out frames."""
    return timeline_tools.get_track_items(track_type, track_index)

@server.tool()
def get_clip_properties(track_type: str = "video", track_index: int = 1, item_index: int = 1, property_key: Optional[str] = None) -> Dict[str, Any]:
    """Inspect clip Inspector properties (Pan, Tilt, ZoomX, ZoomY, Crop, CompositeMode)."""
    return timeline_tools.get_clip_properties(track_type, track_index, item_index, property_key)

@server.tool()
def set_clip_properties(track_type: str = "video", track_index: int = 1, item_index: int = 1, properties: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Set Inspector properties on a clip.
    Supported: Pan, Tilt, ZoomX, ZoomY, RotationAngle, CropLeft, CropRight, CropTop, CropBottom, CompositeMode (0-31), Opacity.
    """
    return timeline_tools.set_clip_properties(track_type, track_index, item_index, properties)

@server.tool()
def add_marker(frame_id: int, color: str = "Blue", name: str = "", note: str = "", duration: int = 1) -> Dict[str, Any]:
    """Add a marker at a timeline frame (e.g. for edit review, chapter points)."""
    return timeline_tools.add_marker(frame_id, color, name, note, duration)

@server.tool()
def get_markers() -> Dict[str, Any]:
    """Get all markers on the active timeline."""
    return timeline_tools.get_markers()

@server.tool()
def delete_marker(frame_id: Optional[int] = None, color: Optional[str] = None) -> Dict[str, Any]:
    """Delete a marker at a specific frame or delete all markers matching a color."""
    return timeline_tools.delete_marker(frame_id, color)


# ==========================================
# 4. Fusion, Titles & Graphics Tools
# ==========================================

@server.tool()
def insert_generator_into_timeline(generator_name: str) -> Dict[str, Any]:
    """Insert a generator into the timeline (e.g. 'Solid Color', '10 Step', 'Grey Scale')."""
    return fusion_graphics_tools.insert_generator_into_timeline(generator_name)

@server.tool()
def insert_title_into_timeline(title_name: str = "Text") -> Dict[str, Any]:
    """Insert a standard title into the active timeline (e.g. 'Text', 'Lower Third')."""
    return fusion_graphics_tools.insert_title_into_timeline(title_name)

@server.tool()
def insert_fusion_title_into_timeline(template_name: str = "Text+") -> Dict[str, Any]:
    """Insert a Fusion Title template into the timeline (e.g. 'Text+', 'Call Out')."""
    return fusion_graphics_tools.insert_fusion_title_into_timeline(template_name)

@server.tool()
def set_text_plus_properties(
    track_index: int = 1,
    item_index: int = 1,
    text: Optional[str] = None,
    font: Optional[str] = None,
    size: Optional[float] = None,
    color_rgb: Optional[List[float]] = None
) -> Dict[str, Any]:
    """Configure text, font family, font size, and RGB color ([r, g, b] 0.0-1.0) on a Text+ clip."""
    return fusion_graphics_tools.set_text_plus_properties(track_index, item_index, text, font, size, color_rgb)

@server.tool()
def get_fusion_comp_tools(track_index: int = 1, item_index: int = 1) -> Dict[str, Any]:
    """List all nodes/tools inside a clip's Fusion composition."""
    return fusion_graphics_tools.get_fusion_comp_tools(track_index, item_index)


# ==========================================
# 5. Audio & Fairlight Tools
# ==========================================

@server.tool()
def get_voice_isolation(track_type: str = "video", track_index: int = 1, item_index: int = 1) -> Dict[str, Any]:
    """Get DaVinci Neural Engine Voice Isolation state on a clip (Studio)."""
    return audio_tools.get_voice_isolation(track_type, track_index, item_index)

@server.tool()
def set_voice_isolation(
    track_type: str = "video",
    track_index: int = 1,
    item_index: int = 1,
    enabled: bool = True,
    amount: int = 65
) -> Dict[str, Any]:
    """Set Voice Isolation (0-100) on a clip to eliminate noise and background chatter (Studio)."""
    return audio_tools.set_voice_isolation(track_type, track_index, item_index, enabled, amount)

@server.tool()
def create_subtitles_from_audio(
    language: Optional[str] = None,
    max_characters_per_line: int = 42,
    lines: str = "Double"
) -> Dict[str, Any]:
    """Trigger DaVinci Resolve Studio speech-to-text automatic subtitle generation."""
    return audio_tools.create_subtitles_from_audio(language, max_characters_per_line, lines)

@server.tool()
def get_fairlight_presets() -> Dict[str, Any]:
    """List saved Fairlight track presets."""
    return audio_tools.get_fairlight_presets()

@server.tool()
def apply_fairlight_preset(preset_name: str) -> Dict[str, Any]:
    """Apply a saved Fairlight audio preset (EQ/Dynamics/FX chain) to the active timeline."""
    return audio_tools.apply_fairlight_preset(preset_name)


# ==========================================
# 6. Color Grading Tools
# ==========================================

@server.tool()
def apply_grade_from_drx(
    drx_path: str,
    grade_mode: int = 0,
    track_index: int = 1,
    item_index: int = 1
) -> Dict[str, Any]:
    """Apply a .drx PowerGrade / Still file to a clip (0=no keyframes, 1=source TC, 2=start frames)."""
    return color_tools.apply_grade_from_drx(drx_path, grade_mode, track_index, item_index)

@server.tool()
def set_clip_cdl(
    track_index: int = 1,
    item_index: int = 1,
    node_index: int = 1,
    slope: Optional[List[float]] = None,
    offset: Optional[List[float]] = None,
    power: Optional[List[float]] = None,
    saturation: Optional[float] = None
) -> Dict[str, Any]:
    """Set CDL color balance values (Slope, Offset, Power, Saturation) on a color node."""
    return color_tools.set_clip_cdl(track_index, item_index, node_index, slope, offset, power, saturation)

@server.tool()
def set_clip_lut(
    track_index: int = 1,
    item_index: int = 1,
    node_index: int = 1,
    lut_path: str = ""
) -> Dict[str, Any]:
    """Apply a 3D LUT (.cube file) to a specific node on a clip."""
    return color_tools.set_clip_lut(track_index, item_index, node_index, lut_path)

@server.tool()
def add_color_version(
    track_index: int = 1,
    item_index: int = 1,
    version_name: str = "Version 2",
    version_type: int = 0
) -> Dict[str, Any]:
    """Add a non-destructive color version (0=local, 1=remote) for look comparison."""
    return color_tools.add_color_version(track_index, item_index, version_name, version_type)

@server.tool()
def list_color_versions(
    track_index: int = 1,
    item_index: int = 1,
    version_type: int = 0
) -> Dict[str, Any]:
    """List color versions on a timeline clip."""
    return color_tools.list_color_versions(track_index, item_index, version_type)


# ==========================================
# 7. Render & Export Tools
# ==========================================

@server.tool()
def get_render_presets() -> Dict[str, Any]:
    """List available render presets (YouTube, ProRes, H.264, etc.)."""
    return render_tools.get_render_presets()

@server.tool()
def load_render_preset(preset_name: str) -> Dict[str, Any]:
    """Load an export preset into the Deliver page configuration."""
    return render_tools.load_render_preset(preset_name)

@server.tool()
def set_render_settings(
    target_dir: str,
    custom_name: str,
    format_name: Optional[str] = None,
    codec_name: Optional[str] = None
) -> Dict[str, Any]:
    """Configure render output directory and target filename."""
    return render_tools.set_render_settings(target_dir, custom_name, format_name, codec_name)

@server.tool()
def add_render_job() -> Dict[str, Any]:
    """Add current export configuration to the Deliver Render Queue."""
    return render_tools.add_render_job()

@server.tool()
def list_render_jobs() -> Dict[str, Any]:
    """List all jobs currently in the Deliver Render Queue."""
    return render_tools.list_render_jobs()

@server.tool()
def start_rendering(job_ids: Optional[List[str]] = None) -> Dict[str, Any]:
    """Start rendering jobs in the queue."""
    return render_tools.start_rendering(job_ids)

@server.tool()
def get_render_status() -> Dict[str, Any]:
    """Get active render status and progress percentage."""
    return render_tools.get_render_status()

@server.tool()
def stop_rendering() -> Dict[str, Any]:
    """Stop/cancel ongoing render."""
    return render_tools.stop_rendering()

@server.tool()
def delete_all_render_jobs() -> Dict[str, Any]:
    """Clear all jobs from the Render Queue."""
    return render_tools.delete_all_render_jobs()


# ==========================================
# 8. Knowledge Base MCP Resources
# ==========================================

@server.resource("resolve-kb://capabilities")
def get_kb_capabilities() -> str:
    """Direct API vs Workarounds vs UI-only capabilities matrix."""
    return read_kb_file("00-capability-matrix.md")

@server.resource("resolve-kb://effects")
def get_kb_effects() -> str:
    """Resolve FX & OpenFX parameters catalog and starting values."""
    return read_kb_file("01-video-effects-resolvefx.md")

@server.resource("resolve-kb://transitions")
def get_kb_transitions() -> str:
    """Video and audio transitions guide."""
    return read_kb_file("02-transitions.md")

@server.resource("resolve-kb://graphics")
def get_kb_graphics() -> str:
    """Titles, generators, Text+, and subtitle automation."""
    return read_kb_file("03-titles-graphics-generators.md")

@server.resource("resolve-kb://fusion")
def get_kb_fusion() -> str:
    """Fusion node wiring, tool IDs, and keyframing in code."""
    return read_kb_file("04-fusion-scripting.md")

@server.resource("resolve-kb://audio")
def get_kb_audio() -> str:
    """Fairlight audio FX, EQ, LUFS loudness, and voice isolation."""
    return read_kb_file("05-audio-fairlight.md")

@server.resource("resolve-kb://color")
def get_kb_color() -> str:
    """Color grading, node trees, CDL, LUTs, and DRX grades."""
    return read_kb_file("06-color-grading.md")

@server.resource("resolve-kb://inspector")
def get_kb_inspector() -> str:
    """TimelineItem.SetProperty keys and value ranges reference."""
    return read_kb_file("07-inspector-properties.md")

@server.resource("resolve-kb://recipes")
def get_kb_recipes() -> str:
    """End-to-end recipes for YouTube, Podcasts, Social Reels."""
    return read_kb_file("08-recipes.md")

@server.resource("resolve-kb://readme")
def get_kb_readme() -> str:
    """Knowledge base overview and agent rules."""
    return read_kb_file("README.md")

@server.resource("resolve-kb://api-reference")
def get_kb_api_reference() -> str:
    """Raw DaVinci Resolve Scripting API reference extract."""
    return read_kb_file("api_ref.txt")


# ==========================================
# 9. MCP Workflow Prompts
# ==========================================

@server.prompt()
def youtube_talking_head_workflow(project_name: str, video_file: str) -> str:
    """Prompt template for automated YouTube talking-head video assembly."""
    return f"""Execute the complete YouTube Talking-Head workflow for project '{project_name}' with video file '{video_file}':
1. Check DaVinci Resolve connection with get_resolve_status.
2. Create or open project '{project_name}' and set 1080p 24fps resolution.
3. Ingest '{video_file}' into an 'A-Roll' bin.
4. Create an empty timeline 'Main_Edit_v1' and append the A-Roll footage.
5. Apply Voice Isolation (amount=65) to dialogue track.
6. Trigger create_subtitles_from_audio for automated captions.
7. Prepare a YouTube 1080p render job in the Deliver queue."""

@server.prompt()
def vertical_social_reel_workflow(timeline_name: str) -> str:
    """Prompt template for converting a landscape edit to 9:16 vertical social format."""
    return f"""Execute 9:16 Vertical Social format conversion for timeline '{timeline_name}':
1. Duplicate '{timeline_name}' to '{timeline_name}_Vertical_9x16' for non-destructive editing.
2. Switch active timeline to the duplicate.
3. Configure timeline resolution to 1080x1920 (9:16 vertical).
4. Inspect clips and adjust Pan, Tilt, and ZoomX/ZoomY using set_clip_properties to frame the subject.
5. Generate open captions using create_subtitles_from_audio.
6. Configure H.264 MP4 export."""


if __name__ == "__main__":
    # Run server with stdio transport for local AI clients (Claude Desktop, Cursor, etc.)
    server.run(transport="stdio")
