import os
import sys
import platform
from typing import Any, Optional, Dict

class ResolveBridge:
    """
    Manages the connection to the DaVinci Resolve Scripting API.
    Supports macOS, Windows, and Linux.
    """

    def __init__(self):
        self._resolve = None
        self._fusion = None
        self._initialized = False
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

    def connect(self) -> bool:
        """Attempts to connect to a running DaVinci Resolve instance."""
        try:
            import DaVinciResolveScript as dvr_script
            self._resolve = dvr_script.scriptapp("Resolve")
            self._fusion = dvr_script.scriptapp("Fusion")
            self._initialized = self._resolve is not None
            return self._initialized
        except Exception:
            self._resolve = None
            self._fusion = None
            self._initialized = False
            return False

    def get_resolve(self) -> Any:
        """Returns the active Resolve object or raises an informative error."""
        if self._resolve is None or not self._initialized:
            if not self.connect():
                raise ConnectionError(
                    "Could not connect to DaVinci Resolve.\n"
                    "Please verify:\n"
                    "1. DaVinci Resolve (Studio or compatible) is running.\n"
                    "2. In DaVinci Resolve Preferences > General > External scripting using, select 'Local' or 'Network'.\n"
                    "3. If DaVinci Resolve is installed in a non-default directory, set RESOLVE_SCRIPT_API and RESOLVE_SCRIPT_LIB environment variables."
                )
        return self._resolve

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
        """Returns diagnostic and environment status."""
        connected = self.connect()
        if not connected:
            return {
                "connected": False,
                "error": "DaVinci Resolve is not running or external scripting is disabled in Preferences.",
                "os": platform.system(),
                "script_api": os.getenv("RESOLVE_SCRIPT_API"),
                "script_lib": os.getenv("RESOLVE_SCRIPT_LIB"),
            }

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
                "product_name": product,
                "version": version,
                "current_project": proj_name,
                "current_timeline": timeline_name,
                "timeline_count": current_project.GetTimelineCount() if current_project else 0,
            }
        except Exception as e:
            return {
                "connected": True,
                "partial_error": str(e)
            }

bridge = ResolveBridge()
