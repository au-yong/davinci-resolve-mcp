import os
import sys
import json
import platform
import urllib.request
import urllib.error
from typing import Any, Optional, Dict

class ResolveBridge:
    """
    Manages the connection to the DaVinci Resolve Scripting API.
    Supports BOTH DaVinci Resolve Studio (direct external API)
    and DaVinci Resolve Free (in-app loopback bridge).
    """

    def __init__(self):
        self._resolve = None
        self._fusion = None
        self._initialized = False
        self._mode = None  # 'direct' (Studio external) or 'bridge' (In-App loopback)
        self._bridge_port = int(os.getenv("DAVINCI_RESOLVE_BRIDGE_PORT", "9099"))
        self._bridge_url = f"http://127.0.0.1:{self._bridge_port}"
        self._init_environment()

    def _init_environment(self) -> None:
        """Sets up the necessary environment paths for DaVinciResolveScript."""
        current_os = platform.system()
        api_path = os.getenv("RESOLVE_SCRIPT_API")
        lib_path = os.getenv("RESOLVE_SCRIPT_LIB")

        if current_os == "Darwin":  # macOS
            if not api_path:
                api_path = "/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting"
            if not lib_path:
                lib_path = "/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Libraries/Fusion/fusionscript.so"
        elif current_os == "Windows":
            program_data = os.getenv("PROGRAMDATA", "C:\\ProgramData")
            program_files = os.getenv("PROGRAMFILES", "C:\\Program Files")
            if not api_path:
                api_path = os.path.join(program_data, "Blackmagic Design", "DaVinci Resolve", "Support", "Developer", "Scripting")
            if not lib_path:
                lib_path = os.path.join(program_files, "Blackmagic Design", "DaVinci Resolve", "fusionscript.dll")
        elif current_os == "Linux":
            if not api_path:
                api_path = "/opt/resolve/Developer/Scripting"
            if not lib_path:
                lib_path = "/opt/resolve/libs/Fusion/fusionscript.so"

        if api_path:
            os.environ["RESOLVE_SCRIPT_API"] = api_path
            modules_path = os.path.join(api_path, "Modules")
            if os.path.exists(modules_path) and modules_path not in sys.path:
                sys.path.append(modules_path)

        if lib_path:
            os.environ["RESOLVE_SCRIPT_LIB"] = lib_path

    def set_resolve(self, resolve_obj: Any, fusion_obj: Any = None) -> None:
        """Injects live Resolve instance (used when running inside DaVinci Resolve)."""
        self._resolve = resolve_obj
        self._fusion = fusion_obj
        self._initialized = resolve_obj is not None
        self._mode = "direct"

    @property
    def is_bridge_mode(self) -> bool:
        """Returns True if communicating via in-app bridge (Python loopback or Lua IPC)."""
        if not self._initialized:
            self.connect()
        return self._mode in ("bridge", "python_bridge", "lua_bridge")

    def _check_bridge_health(self) -> bool:
        """Checks if the in-app loopback bridge is responding."""
        try:
            req = urllib.request.Request(
                f"{self._bridge_url}/health",
                headers={"User-Agent": "DVR-MCP-Client"}
            )
            with urllib.request.urlopen(req, timeout=0.6) as resp:
                return resp.status == 200
        except Exception:
            return False

    def _get_ipc_dir(self) -> str:
        """Returns the IPC directory path used by the Lua In-App bridge."""
        home = os.path.expanduser("~")
        ipc_dir = os.path.join(home, ".davinci_resolve_mcp_ipc")
        os.makedirs(ipc_dir, exist_ok=True)
        return ipc_dir

    def _check_lua_bridge_health(self) -> bool:
        """Checks if the Lua in-app bridge is active via status.json."""
        try:
            status_file = os.path.join(self._get_ipc_dir(), "status.json")
            if not os.path.exists(status_file):
                return False
            # Check modification time within last 60 seconds
            mtime = os.path.getmtime(status_file)
            import time
            if time.time() - mtime < 60.0:
                return True
            with open(status_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return bool(data.get("connected"))
        except Exception:
            return False

    def connect(self) -> bool:
        """
        Attempts to connect to DaVinci Resolve:
        1. If DAVINCI_RESOLVE_BRIDGE=lua: connects via Lua IPC bridge.
        2. If DAVINCI_RESOLVE_BRIDGE=1: connects via Python HTTP bridge.
        3. Tries native external API (DaVinci Resolve Studio).
        4. Tries Python in-app loopback bridge (http://127.0.0.1:9099).
        5. Tries Lua in-app IPC bridge (~/.davinci_resolve_mcp_ipc/).
        """
        # If already directly set
        if self._resolve is not None and self._mode == "direct":
            self._initialized = True
            return True

        force_bridge = os.getenv("DAVINCI_RESOLVE_BRIDGE")

        if force_bridge == "lua":
            if self._check_lua_bridge_health():
                self._mode = "lua_bridge"
                self._initialized = True
                return True

        if force_bridge not in ("1", "lua"):
            # Step 1: Attempt native external scripting (Studio)
            try:
                import DaVinciResolveScript as dvr_script
                self._resolve = dvr_script.scriptapp("Resolve")
                self._fusion = dvr_script.scriptapp("Fusion")
                if self._resolve is not None:
                    self._mode = "direct"
                    self._initialized = True
                    return True
            except Exception:
                pass

        # Step 2: Attempt Python In-App loopback bridge
        if self._check_bridge_health():
            self._mode = "python_bridge"
            self._initialized = True
            return True

        # Step 3: Attempt Lua In-App IPC bridge
        if self._check_lua_bridge_health():
            self._mode = "lua_bridge"
            self._initialized = True
            return True

        self._resolve = None
        self._fusion = None
        self._mode = None
        self._initialized = False
        return False

    def call_bridge(self, tool_name: str, kwargs: Optional[Dict[str, Any]] = None) -> Any:
        """Forwards a tool call to the active in-app bridge (Python HTTP or Lua IPC)."""
        if kwargs is None:
            kwargs = {}

        if self._mode == "lua_bridge":
            return self.call_lua_bridge(tool_name, kwargs)

        return self.call_python_bridge(tool_name, kwargs)

    def call_python_bridge(self, tool_name: str, kwargs: Dict[str, Any]) -> Any:
        """Forwards a tool call via loopback HTTP to davinci_resolve_mcp_bridge.py."""
        payload = json.dumps({"tool": tool_name, "kwargs": kwargs}).encode("utf-8")
        req = urllib.request.Request(
            f"{self._bridge_url}/execute",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "DVR-MCP-Client"
            }
        )

        try:
            with urllib.request.urlopen(req, timeout=30.0) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                if not data.get("success", False):
                    err = data.get("error", "Unknown error in DaVinci Resolve in-app bridge.")
                    return {"success": False, "error": err}
                return data.get("result")
        except urllib.error.URLError as e:
            return {
                "success": False,
                "error": (
                    f"Failed to communicate with DaVinci Resolve In-App Bridge ({e}).\n"
                    "Please ensure DaVinci Resolve is open and the bridge is active at: "
                    "Workspace > Scripts > Utility > davinci_resolve_mcp_bridge"
                )
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def call_lua_bridge(self, tool_name: str, kwargs: Dict[str, Any]) -> Any:
        """Forwards a tool call via file IPC to davinci_resolve_mcp_bridge.lua."""
        import time
        ipc_dir = self._get_ipc_dir()
        req_file = os.path.join(ipc_dir, "request.json")
        req_tmp = os.path.join(ipc_dir, "request.json.tmp")
        resp_file = os.path.join(ipc_dir, "response.json")

        # Clear any stale response
        if os.path.exists(resp_file):
            try:
                os.remove(resp_file)
            except Exception:
                pass

        payload = json.dumps({"tool": tool_name, "kwargs": kwargs, "time": time.time()})
        with open(req_tmp, "w", encoding="utf-8") as f:
            f.write(payload)
        os.replace(req_tmp, req_file)

        # Wait for response (up to 15s)
        start_time = time.time()
        while time.time() - start_time < 15.0:
            if os.path.exists(resp_file):
                try:
                    with open(resp_file, "r", encoding="utf-8") as f:
                        resp_content = f.read().strip()
                    if resp_content:
                        try:
                            os.remove(resp_file)
                        except Exception:
                            pass
                        data = json.loads(resp_content)
                        if not data.get("success", False):
                            return {"success": False, "error": data.get("error", "Error in Lua bridge")}
                        return data.get("result")
                except json.JSONDecodeError:
                    pass  # File still being written, retry
            time.sleep(0.05)

        return {
            "success": False,
            "error": "Timeout waiting for DaVinci Resolve Lua Bridge response (~/.davinci_resolve_mcp_ipc/)."
        }

    def get_resolve(self) -> Any:
        """Returns the active Resolve object or raises an informative error."""
        if not self._initialized:
            self.connect()

        if self._mode == "direct" and self._resolve is not None:
            return self._resolve

        if self._mode in ("bridge", "python_bridge", "lua_bridge"):
            raise RuntimeError(
                "Resolve is running in In-App Bridge mode (Free edition). "
                "Direct Python object access is proxied through call_bridge()."
            )

        raise ConnectionError(
            "Could not connect to DaVinci Resolve.\n\n"
            "▶ FOR DAVINCI RESOLVE STUDIO:\n"
            "  1. Ensure DaVinci Resolve Studio is running.\n"
            "  2. Go to Preferences > System > General > External scripting using, and select 'Local'.\n\n"
            "▶ FOR DAVINCI RESOLVE (FREE VERSION):\n"
            "  1. Run 'python install_bridge.py' to install the in-app bridge script.\n"
            "  2. In DaVinci Resolve, go to: Workspace > Scripts > Utility > davinci_resolve_mcp_bridge (.lua or .py)\n"
            "  3. Open your project."
        )

    def get_fusion(self) -> Any:
        """Returns the Fusion application object."""
        self.get_resolve()
        return self._fusion

    def get_project_manager(self) -> Any:
        """Returns the ProjectManager object."""
        resolve = self.get_resolve()
        pm = resolve.GetProjectManager()
        if not pm:
            raise RuntimeError("Failed to obtain ProjectManager from DaVinci Resolve.")
        return pm

    def get_current_project(self) -> Any:
        """Returns the currently active Project object."""
        pm = self.get_project_manager()
        proj = pm.GetCurrentProject()
        if not proj:
            raise RuntimeError("No project is currently open in DaVinci Resolve.")
        return proj

    def get_media_pool(self) -> Any:
        """Returns the MediaPool object for current project."""
        project = self.get_current_project()
        mp = project.GetMediaPool()
        if not mp:
            raise RuntimeError("Failed to obtain MediaPool for current project.")
        return mp

    def get_current_timeline(self) -> Any:
        """Returns the currently active Timeline object."""
        project = self.get_current_project()
        timeline = project.GetCurrentTimeline()
        if not timeline:
            raise RuntimeError("No timeline is currently active in the open project.")
        return timeline

    def get_status(self) -> Dict[str, Any]:
        """Returns diagnostic and environment status for Studio, Python bridge, and Lua bridge."""
        connected = self.connect()

        if not connected:
            return {
                "connected": False,
                "error": (
                    "Could not connect to DaVinci Resolve.\n\n"
                    "▶ FOR DAVINCI RESOLVE STUDIO:\n"
                    "  - Launch DaVinci Resolve Studio.\n"
                    "  - Ensure Preferences > General > External scripting using is set to 'Local'.\n\n"
                    "▶ FOR DAVINCI RESOLVE (FREE EDITION):\n"
                    "  - Run: python install_bridge.py\n"
                    "  - In DaVinci Resolve top menu, click:\n"
                    "      Workspace > Scripts > Utility > davinci_resolve_mcp_bridge (.lua or .py)\n"
                    "  - Keep DaVinci Resolve running with an open project."
                ),
                "os": platform.system(),
                "bridge_url": self._bridge_url,
                "ipc_dir": self._get_ipc_dir(),
                "script_api": os.getenv("RESOLVE_SCRIPT_API"),
                "script_lib": os.getenv("RESOLVE_SCRIPT_LIB"),
            }

        # If connected via Lua In-App IPC bridge
        if self._mode == "lua_bridge":
            try:
                status_file = os.path.join(self._get_ipc_dir(), "status.json")
                with open(status_file, "r", encoding="utf-8") as f:
                    lua_data = json.load(f)
                lua_data["mode"] = "in_app_lua_bridge (Free & Studio)"
                lua_data["ipc_dir"] = self._get_ipc_dir()
                return lua_data
            except Exception as e:
                return {
                    "connected": True,
                    "mode": "in_app_lua_bridge",
                    "ipc_dir": self._get_ipc_dir(),
                    "warning": f"Lua bridge is active but status read failed: {e}"
                }

        # If connected via Python in-app loopback bridge
        if self._mode in ("bridge", "python_bridge"):
            try:
                req = urllib.request.Request(f"{self._bridge_url}/status")
                with urllib.request.urlopen(req, timeout=1.5) as resp:
                    bridge_data = json.loads(resp.read().decode("utf-8"))
                    bridge_data["mode"] = "in_app_python_bridge (Free & Studio)"
                    bridge_data["bridge_url"] = self._bridge_url
                    return bridge_data
            except Exception as e:
                return {
                    "connected": True,
                    "mode": "in_app_python_bridge",
                    "bridge_url": self._bridge_url,
                    "warning": f"Bridge is responsive but status query failed: {e}"
                }

        # If connected via native external API (Studio)
        try:
            version = self._resolve.GetVersionString()
            product = self._resolve.GetProductName()
            pm = self._resolve.GetProjectManager()
            current_project = pm.GetCurrentProject() if pm else None
            proj_name = current_project.GetName() if current_project else None
            current_timeline = current_project.GetCurrentTimeline() if current_project else None
            timeline_name = current_timeline.GetName() if current_timeline else None

            return {
                "connected": True,
                "mode": "direct (Studio external)",
                "product_name": product,
                "version": version,
                "current_project": proj_name,
                "current_timeline": timeline_name,
                "timeline_count": current_project.GetTimelineCount() if current_project else 0,
            }
        except Exception as e:
            return {
                "connected": True,
                "mode": "direct (Studio external)",
                "partial_error": str(e)
            }

bridge = ResolveBridge()


