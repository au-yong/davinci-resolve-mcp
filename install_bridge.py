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
    bridge_src = repo_root / "davinci_resolve_mcp_bridge.py"

    if not bridge_src.exists():
        print(f"❌ Error: Could not find '{bridge_src}'. Make sure you run this script from the DavinciResolveMCP directory.")
        sys.exit(1)

    # 1. Record repo root so the bridge script can always find the tools package
    cfg_file = Path.home() / ".davinci_resolve_mcp_root"
    try:
        with open(cfg_file, "w", encoding="utf-8") as f:
            f.write(str(repo_root))
        print(f"📁 Registered repository root: {repo_root}")
    except Exception as e:
        print(f"⚠️ Could not write {cfg_file}: {e}")

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

    target_file = target_dir / "davinci_resolve_mcp_bridge.py"

    try:
        shutil.copy2(bridge_src, target_file)
        # Ensure executable permissions on Unix
        if platform.system() != "Windows":
            target_file.chmod(0o755)
    except Exception as e:
        print(f"❌ Failed to copy bridge to '{target_file}': {e}")
        sys.exit(1)

    print("\n" + "=" * 68)
    print(" 🎉 DaVinci Resolve MCP In-App Bridge Installed Successfully!")
    print("=" * 68)
    print(f" Installed to: {target_file}\n")
    print(" 🚀 HOW TO USE WITH DAVINCI RESOLVE (FREE & STUDIO EDITIONS):")
    print(" 1. Launch DaVinci Resolve and open any project.")
    print(" 2. In the top menu bar, navigate to:")
    print("      Workspace > Scripts > Utility > davinci_resolve_mcp_bridge")
    print(" 3. A console message will confirm:")
    print("      'Active & Listening on http://127.0.0.1:9099'")
    print(" 4. Keep DaVinci Resolve open.")
    print(" ")
    print(" 💬 Your AI assistants (Claude Desktop, Cursor, etc.) can now control")
    print("    DaVinci Resolve seamlessly via standard MCP tools!")
    print("=" * 68 + "\n")

if __name__ == "__main__":
    install_bridge()
