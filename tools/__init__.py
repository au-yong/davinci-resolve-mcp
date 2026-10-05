# DavinciResolveMCP tools package
import functools
import inspect
from resolve_bridge import bridge

from . import project_tools
from . import media_pool_tools
from . import timeline_tools
from . import fusion_graphics_tools
from . import audio_tools
from . import color_tools
from . import render_tools

_TOOL_MODULES = [
    project_tools,
    media_pool_tools,
    timeline_tools,
    fusion_graphics_tools,
    audio_tools,
    color_tools,
    render_tools,
]

def _wrap_tool(orig_func, name: str):
    sig = inspect.signature(orig_func)
    @functools.wraps(orig_func)
    def wrapper(*args, **kwargs):
        # When communicating with DaVinci Resolve Free edition via In-App Bridge
        if bridge.is_bridge_mode:
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()
            return bridge.call_bridge(name, bound.arguments)
        return orig_func(*args, **kwargs)
    return wrapper

# Wrap all public tool functions for automatic dispatch
for mod in _TOOL_MODULES:
    for attr in dir(mod):
        if not attr.startswith("_"):
            val = getattr(mod, attr)
            if callable(val):
                setattr(mod, attr, _wrap_tool(val, attr))
