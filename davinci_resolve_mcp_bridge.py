#!/usr/bin/env python3
"""
DaVinci Resolve MCP In-App Bridge
=================================
Enables Model Context Protocol (MCP) support for BOTH DaVinci Resolve Free and Studio editions.

How it works:
- In DaVinci Resolve Studio: External Python scripting is supported directly.
- In DaVinci Resolve Free: External process scripting is restricted by Blackmagic Design,
  but internal scripts triggered via Workspace > Scripts have full access to the live
  DaVinci Resolve API.
- This script runs inside DaVinci Resolve as a background loopback listener (http://127.0.0.1:9099).
- External AI clients (Claude Desktop, Cursor, etc.) communicate through the MCP server,
  which seamlessly forwards tool calls to this in-app bridge when in Free edition mode.

Usage inside DaVinci Resolve:
1. Go to top menu: Workspace > Scripts > Utility > davinci_resolve_mcp_bridge
2. The bridge starts listening on 127.0.0.1:9099.
3. Open any project and timeline. Your AI assistant is now connected!
"""

import os
import sys
import json
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.request
import urllib.error

BRIDGE_PORT = int(os.getenv("DAVINCI_RESOLVE_BRIDGE_PORT", "9099"))
BRIDGE_HOST = "127.0.0.1"  # Loopback only for security

def get_resolve_instance():
    """Acquires the active Resolve object within DaVinci Resolve's runtime."""
    # 1. Global variable injected by Resolve when running from Workspace > Scripts
    if "resolve" in globals() and globals()["resolve"] is not None:
        return globals()["resolve"]

    # 2. app.GetResolve() available in some Resolve internal scopes
    if "app" in globals() and hasattr(globals()["app"], "GetResolve"):
        try:
            r = globals()["app"].GetResolve()
            if r:
                return r
        except Exception:
            pass

    # 3. bmd.scriptapp("Resolve") in Blackmagic Fusion / Resolve runtime
    if "bmd" in globals() and hasattr(globals()["bmd"], "scriptapp"):
        try:
            r = globals()["bmd"].scriptapp("Resolve")
            if r:
                return r
        except Exception:
            pass

    # 4. Standard DaVinciResolveScript fallback
    try:
        import DaVinciResolveScript as dvr
        r = dvr.scriptapp("Resolve")
        if r:
            return r
    except Exception:
        pass

    return None

def get_fusion_instance():
    """Acquires Fusion object if available."""
    if "fusion" in globals() and globals()["fusion"] is not None:
        return globals()["fusion"]
    if "bmd" in globals() and hasattr(globals()["bmd"], "scriptapp"):
        try:
            return globals()["bmd"].scriptapp("Fusion")
        except Exception:
            pass
    try:
        import DaVinciResolveScript as dvr
        return dvr.scriptapp("Fusion")
    except Exception:
        return None

def find_repo_root():
    """Locate the DavinciResolveMCP project root to import tool implementations."""
    # 1. Explicit env var
    env_root = os.getenv("DAVINCI_RESOLVE_MCP_ROOT")
    if env_root and os.path.exists(env_root):
        return env_root

    # 2. Saved path file ~/.davinci_resolve_mcp_root
    cfg_file = os.path.expanduser("~/.davinci_resolve_mcp_root")
    if os.path.exists(cfg_file):
        try:
            with open(cfg_file, "r", encoding="utf-8") as f:
                saved = f.read().strip()
                if os.path.exists(saved):
                    return saved
        except Exception:
            pass

    # 3. Current script directory or parent directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if os.path.exists(os.path.join(script_dir, "server.py")):
        return script_dir
    parent = os.path.dirname(script_dir)
    if os.path.exists(os.path.join(parent, "server.py")):
        return parent

    return script_dir

# Initialize Resolve Bridge
repo_root = find_repo_root()
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

resolve_obj = get_resolve_instance()
fusion_obj = get_fusion_instance()

try:
    import resolve_bridge
    if resolve_obj:
        resolve_bridge.bridge.set_resolve(resolve_obj, fusion_obj)
except Exception as e:
    print(f"[DaVinci Resolve MCP Bridge] Warning setting resolve_bridge: {e}")

# Build tool function registry from tools package
TOOL_REGISTRY = {}
try:
    from tools import (
        project_tools,
        media_pool_tools,
        timeline_tools,
        fusion_graphics_tools,
        audio_tools,
        color_tools,
        render_tools,
    )
    for mod in [project_tools, media_pool_tools, timeline_tools,
                fusion_graphics_tools, audio_tools, color_tools, render_tools]:
        for attr in dir(mod):
            if not attr.startswith("_"):
                val = getattr(mod, attr)
                if callable(val):
                    # We store the raw un-dispatched tool implementation
                    TOOL_REGISTRY[attr] = val
except Exception as e:
    print(f"[DaVinci Resolve MCP Bridge] Warning importing tools: {e}")

from http.server import HTTPServer

class BridgeHTTPHandler(BaseHTTPRequestHandler):
    """Handles local loopback requests from DavinciResolveMCP server."""

    def log_message(self, format, *args):
        # Keep Resolve console clean
        pass

    def _send_json(self, data, status_code=200):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "127.0.0.1")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path in ("/", "/status"):
            r = get_resolve_instance()
            if r:
                try:
                    version = r.GetVersionString()
                    product = r.GetProductName()
                    pm = r.GetProjectManager()
                    proj = pm.GetCurrentProject() if pm else None
                    proj_name = proj.GetName() if proj else None
                    tl = proj.GetCurrentTimeline() if proj else None
                    tl_name = tl.GetName() if tl else None
                    tl_count = proj.GetTimelineCount() if proj else 0
                    self._send_json({
                        "connected": True,
                        "bridge_mode": "in_app_bridge",
                        "product_name": product,
                        "version": version,
                        "current_project": proj_name,
                        "current_timeline": tl_name,
                        "timeline_count": tl_count,
                        "tools_loaded": len(TOOL_REGISTRY)
                    })
                    return
                except Exception as e:
                    self._send_json({
                        "connected": True,
                        "bridge_mode": "in_app_bridge",
                        "partial_error": str(e)
                    })
                    return

            self._send_json({
                "connected": False,
                "bridge_mode": "in_app_bridge",
                "error": "Resolve instance not found inside DaVinci Resolve. Please open a project."
            })
        elif self.path in ("/health", "/ping"):
            self._send_json({"status": "ok", "tools_loaded": len(TOOL_REGISTRY)})
        else:
            self._send_json({"error": "Endpoint not found"}, 404)

    def do_POST(self):
        if self.path == "/execute":
            try:
                content_len = int(self.headers.get("Content-Length", 0))
                raw_body = self.rfile.read(content_len).decode("utf-8")
                payload = json.loads(raw_body)

                tool_name = payload.get("tool")
                kwargs = payload.get("kwargs", {})

                if not tool_name or tool_name not in TOOL_REGISTRY:
                    self._send_json({
                        "success": False,
                        "error": f"Tool '{tool_name}' not found in Bridge Tool Registry."
                    }, 404)
                    return

                # Ensure resolve reference is fresh
                r = get_resolve_instance()
                if r:
                    resolve_bridge.bridge.set_resolve(r, get_fusion_instance())

                # Execute tool function inside Resolve's process
                func = TOOL_REGISTRY[tool_name]
                result = func(**kwargs)
                self._send_json({"success": True, "result": result})

            except Exception as e:
                self._send_json({"success": False, "error": str(e)}, 500)

        elif self.path == "/stop":
            self._send_json({"success": True, "message": "Bridge is stopping."})
            threading.Thread(target=self.server.shutdown).start()
        else:
            self._send_json({"error": "Endpoint not found"}, 404)

def check_already_running(port: int) -> bool:
    """Check if bridge server is already active on this port."""
    url = f"http://{BRIDGE_HOST}:{port}/health"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "DVR-Bridge-Check"})
        with urllib.request.urlopen(req, timeout=0.8) as resp:
            return resp.status == 200
    except Exception:
        return False

def start_server(port: int = BRIDGE_PORT):
    """Starts the in-app HTTP listener in a background thread."""
    if check_already_running(port):
        print(f"[DaVinci Resolve MCP Bridge] Already running and active on http://{BRIDGE_HOST}:{port}")
        return

    try:
        httpd = HTTPServer((BRIDGE_HOST, port), BridgeHTTPHandler)
    except Exception as e:
        print(f"[DaVinci Resolve MCP Bridge] Failed to bind to port {port}: {e}")
        return

    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()

    r = get_resolve_instance()
    prod = r.GetProductName() if r else "DaVinci Resolve"
    ver = r.GetVersionString() if r else "Unknown Version"

    print("=" * 64)
    print(" 🎬 DaVinci Resolve MCP In-App Bridge (Free & Studio Edition)")
    print("=" * 64)
    print(f" Status:       Active & Listening on http://{BRIDGE_HOST}:{port}")
    print(f" Product:      {prod}")
    print(f" Version:      {ver}")
    print(f" Tools Loaded: {len(TOOL_REGISTRY)} / 49")
    print(f" Transport:    Loopback ({BRIDGE_HOST})")
    print(" ")
    print(" ✅ Ready! Your AI assistant (Claude, Cursor, etc.) can now")
    print("    control DaVinci Resolve directly.")
    print("=" * 64)

if __name__ == "__main__" or "resolve" in globals() or "app" in globals() or "bmd" in globals():
    start_server(BRIDGE_PORT)
