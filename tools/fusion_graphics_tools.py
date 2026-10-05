from typing import Any, Dict, List, Optional
from resolve_bridge import bridge

def insert_generator_into_timeline(generator_name: str) -> Dict[str, Any]:
    """
    Insert a built-in generator into the timeline (e.g. 'Solid Color', '10 Step', 'Grey Scale', 'Window').
    """
    timeline = bridge.get_current_timeline()
    item = timeline.InsertGeneratorIntoTimeline(generator_name)
    if not item:
        return {"success": False, "error": f"Failed to insert generator '{generator_name}'. Check exact generator name."}
    return {"success": True, "item_name": item.GetName(), "generator": generator_name}

def insert_title_into_timeline(title_name: str = "Text") -> Dict[str, Any]:
    """
    Insert a standard title into the active timeline (e.g. 'Text', 'Scroll', 'Lower Third').
    """
    timeline = bridge.get_current_timeline()
    item = timeline.InsertTitleIntoTimeline(title_name)
    if not item:
        return {"success": False, "error": f"Failed to insert title '{title_name}'. Verify title name in Effects Library."}
    return {"success": True, "item_name": item.GetName(), "title": title_name}

def insert_fusion_title_into_timeline(template_name: str = "Text+") -> Dict[str, Any]:
    """
    Insert a Fusion Title template into the active timeline (e.g. 'Text+', 'Call Out', 'Digital Glitch Title').
    """
    timeline = bridge.get_current_timeline()
    item = timeline.InsertFusionTitleIntoTimeline(template_name)
    if not item:
        return {"success": False, "error": f"Failed to insert Fusion title '{template_name}'."}
    return {"success": True, "item_name": item.GetName(), "template": template_name}

def set_text_plus_properties(
    track_index: int = 1,
    item_index: int = 1,
    text: Optional[str] = None,
    font: Optional[str] = None,
    size: Optional[float] = None,
    color_rgb: Optional[List[float]] = None
) -> Dict[str, Any]:
    """
    Configure text, font, size, and color on a Text+ or Fusion title clip via its Fusion composition.
    color_rgb should be [r, g, b] with values in range 0.0 to 1.0.
    """
    timeline = bridge.get_current_timeline()
    items = timeline.GetItemListInTrack("video", track_index) or []
    if not (1 <= item_index <= len(items)):
        return {"success": False, "error": f"Item index {item_index} out of range on video track {track_index}."}

    item = items[item_index - 1]
    comp_count = item.GetFusionCompCount()
    if comp_count == 0:
        return {"success": False, "error": f"Clip '{item.GetName()}' has no Fusion compositions."}

    comp = item.GetFusionCompByIndex(1)
    if not comp:
        return {"success": False, "error": "Could not access Fusion composition on clip."}

    tools = comp.GetToolList() or {}
    text_tool = None
    for tool_name, tool in tools.items():
        # Look for TextPlus or Template node
        attrs = tool.GetAttrs() if hasattr(tool, "GetAttrs") else {}
        tool_id = attrs.get("TOOLS_RegID", "")
        if "TextPlus" in tool_id or "TextPlus" in str(tool_name) or "Template" in str(tool_name):
            text_tool = tool
            break

    if not text_tool:
        # Fallback: check first tool with StyledText input
        for tool_name, tool in tools.items():
            inputs = tool.GetInputList() or {}
            if "StyledText" in inputs:
                text_tool = tool
                break

    if not text_tool:
        return {"success": False, "error": "No TextPlus tool found in the Fusion composition."}

    applied = {}
    if text is not None:
        try:
            text_tool.StyledText = text
            applied["text"] = text
        except Exception:
            text_tool.SetInput("StyledText", text)
            applied["text"] = text

    if font is not None:
        try:
            text_tool.Font = font
            applied["font"] = font
        except Exception:
            text_tool.SetInput("Font", font)
            applied["font"] = font

    if size is not None:
        try:
            text_tool.Size = float(size)
            applied["size"] = float(size)
        except Exception:
            text_tool.SetInput("Size", float(size))
            applied["size"] = float(size)

    if color_rgb is not None and len(color_rgb) == 3:
        r, g, b = [float(c) for c in color_rgb]
        try:
            text_tool.Red = r
            text_tool.Green = g
            text_tool.Blue = b
            applied["color_rgb"] = [r, g, b]
        except Exception:
            text_tool.SetInput("Red", r)
            text_tool.SetInput("Green", g)
            text_tool.SetInput("Blue", b)
            applied["color_rgb"] = [r, g, b]

    return {
        "success": True,
        "clip_name": item.GetName(),
        "tool_name": text_tool.Name if hasattr(text_tool, "Name") else "TextPlus",
        "applied": applied
    }

def get_fusion_comp_tools(track_index: int = 1, item_index: int = 1) -> Dict[str, Any]:
    """List all nodes/tools inside a clip's Fusion composition."""
    timeline = bridge.get_current_timeline()
    items = timeline.GetItemListInTrack("video", track_index) or []
    if not (1 <= item_index <= len(items)):
        return {"success": False, "error": f"Item index {item_index} out of range on video track {track_index}."}

    item = items[item_index - 1]
    if item.GetFusionCompCount() == 0:
        return {"success": False, "error": f"Clip '{item.GetName()}' has no Fusion composition."}

    comp = item.GetFusionCompByIndex(1)
    tools = comp.GetToolList() or {}
    tool_info = []
    for name, tool in tools.items():
        attrs = tool.GetAttrs() if hasattr(tool, "GetAttrs") else {}
        tool_info.append({
            "name": str(name),
            "tool_id": attrs.get("TOOLS_RegID", "Unknown")
        })

    return {
        "success": True,
        "clip_name": item.GetName(),
        "tool_count": len(tool_info),
        "tools": tool_info
    }
