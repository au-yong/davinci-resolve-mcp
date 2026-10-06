#!/usr/bin/env python3
"""
DaVinci Resolve MCP - In-App Bridge Installer
=============================================
Installs the In-App Bridge into DaVinci Resolve's Scripts directory.
This enables full MCP automation for BOTH DaVinci Resolve Free and Studio editions.

Usage:
    python install_bridge.py
"""

import os
import sys
import shutil
import platform
from pathlib import Path

def get_resolve_script_dirs():
    """Returns candidate DaVinci Resolve Fusion/Scripts/Utility directories for the current OS."""
    system = platform.system()
    home = Path.home()
    dirs = []

    if system == "Darwin":  # macOS
        dirs.append(home / "Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Scripts/Utility")
        dirs.append(Path("/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Scripts/Utility"))
    elif system == "Windows":
        appdata = os.getenv("APPDATA")
        if appdata:
            dirs.append(Path(appdata) / "Blackmagic Design/DaVinci Resolve/Support/Fusion/Scripts/Utility")
        progdata = os.getenv("PROGRAMDATA", "C:\\ProgramData")
        dirs.append(Path(progdata) / "Blackmagic Design/DaVinci Resolve/Fusion/Scripts/Utility")
    elif system == "Linux":
        dirs.append(home / ".local/share/DaVinciResolve/Fusion/Scripts/Utility")
        dirs.append(Path("/opt/resolve/Fusion/Scripts/Utility"))

    return dirs

def install_bridge():
    repo_root = Path(__file__).resolve().parent
    bridge_py = repo_root / "davinci_resolve_mcp_bridge.py"
    bridge_lua = repo_root / "davinci_resolve_mcp_bridge.lua"

    if not bridge_py.exists() and not bridge_lua.exists():
        print(f"❌ Error: Bridge scripts not found in '{repo_root}'.")
        sys.exit(1)

    # 1. Record repo root so the bridge scripts can always find the tools package
    cfg_file = Path.home() / ".davinci_resolve_mcp_root"
    try:
        with open(cfg_file, "w", encoding="utf-8") as f:
            f.write(str(repo_root))
        print(f"📁 Registered repository root: {repo_root}")
    except Exception as e:
        print(f"⚠️ Could not write {cfg_file}: {e}")

    # Also prepare IPC directory for Lua bridge
    ipc_dir = Path.home() / ".davinci_resolve_mcp_ipc"
    try:
        ipc_dir.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass

    # 2. Find or create target Scripts directory
    candidate_dirs = get_resolve_script_dirs()
    target_dir = candidate_dirs[0]  # Default to user directory

    # Prefer an existing directory if found
    for d in candidate_dirs:
        if d.parent.exists():
            target_dir = d
            break

    try:
        target_dir.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"❌ Could not create directory '{target_dir}': {e}")
        sys.exit(1)

    installed_files = []

    # Copy Python bridge
    if bridge_py.exists():
        target_py = target_dir / "davinci_resolve_mcp_bridge.py"
        try:
            shutil.copy2(bridge_py, target_py)
            if platform.system() != "Windows":
                target_py.chmod(0o755)
            installed_files.append(target_py.name)
        except Exception as e:
            print(f"⚠️ Failed to copy {bridge_py.name}: {e}")

    # Copy Lua bridge
    if bridge_lua.exists():
        target_lua = target_dir / "davinci_resolve_mcp_bridge.lua"
        try:
            shutil.copy2(bridge_lua, target_lua)
            if platform.system() != "Windows":
                target_lua.chmod(0o755)
            installed_files.append(target_lua.name)
        except Exception as e:
            print(f"⚠️ Failed to copy {bridge_lua.name}: {e}")

    print("\n" + "=" * 68)
    print(" 🎉 DaVinci Resolve MCP In-App Bridges Installed Successfully!")
    print("=" * 68)
    print(f" Target Folder: {target_dir}")
    print(f" Installed:     {', '.join(installed_files)}\n")
    print(" 🚀 HOW TO USE WITH DAVINCI RESOLVE (FREE & STUDIO EDITIONS):")
    print(" 1. Launch DaVinci Resolve and open any project.")
    print(" 2. In the top menu bar, click EITHER bridge script:")
    print("      Workspace > Scripts > Utility > davinci_resolve_mcp_bridge.lua   (Native Lua)")
    print("        -- OR --")
    print("      Workspace > Scripts > Utility > davinci_resolve_mcp_bridge.py    (Python)")
    print(" ")
    print(" 💡 Pro-Tip: The .lua version is 100% native with ZERO Python required")
    print("    inside DaVinci Resolve—ideal for the Free edition on any OS!")
    print(" ")
    print(" 3. Keep DaVinci Resolve open.")
    print(" 4. Your AI assistant (Claude, Cursor, Windsurf, etc.) is now connected!")
    print("=" * 68 + "\n")

if __name__ == "__main__":
    install_bridge()
