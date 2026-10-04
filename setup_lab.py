#!/usr/bin/env python3
"""Cross-platform setup helper for the Handshake Cracking Lab."""

from __future__ import annotations

import argparse
import platform
import shutil
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent
MAIN_CPP = REPO_ROOT / "main.cpp"
SRC_DIR = REPO_ROOT / "src"
SRC_MAIN_CPP = SRC_DIR / "main.cpp"
PLATFORMIO_INI = REPO_ROOT / "platformio.ini"


def run(cmd: list[str], *, check: bool = True) -> subprocess.CompletedProcess:
    print("\n$", " ".join(cmd))
    return subprocess.run(cmd, check=check)


def install_platformio() -> None:
    print("Installing/Updating PlatformIO Core...")
    run([sys.executable, "-m", "pip", "install", "--user", "platformio"])


def initialize_project() -> None:
    if not PLATFORMIO_INI.exists():
        print("Initializing PlatformIO project...")
        run([sys.executable, "-m", "platformio", "project", "init", "--board", "esp32dev"])
    else:
        print("platformio.ini already exists; skipping project initialization.")


def copy_source(force: bool) -> None:
    if not MAIN_CPP.exists():
        raise FileNotFoundError(f"Expected {MAIN_CPP} to exist.")

    SRC_DIR.mkdir(parents=True, exist_ok=True)

    if SRC_MAIN_CPP.exists() and not force:
        print("src/main.cpp already exists; skipping copy (use --force-copy to overwrite).")
        return

    shutil.copy2(MAIN_CPP, SRC_MAIN_CPP)
    print(f"Copied {MAIN_CPP.name} -> {SRC_MAIN_CPP}")


def print_aircrack_instructions() -> None:
    os_name = platform.system().lower()
    print("\nInstall aircrack-ng manually on your platform if needed:")

    if os_name == "linux":
        print("- Debian/Ubuntu: sudo apt update && sudo apt install -y aircrack-ng")
        print("- Fedora: sudo dnf install -y aircrack-ng")
        print("- Arch: sudo pacman -S aircrack-ng")
    elif os_name == "darwin":
        print("- macOS (Homebrew): brew install aircrack-ng")
    elif os_name == "windows":
        print("- Windows (Chocolatey): choco install aircrack-ng")
        print("- Windows (Scoop): scoop install aircrack-ng")
    else:
        print("- Check your package manager or build from source: https://www.aircrack-ng.org/")


def main() -> int:
    parser = argparse.ArgumentParser(description="Install dependencies and set up this lab.")
    parser.add_argument(
        "--force-copy",
        action="store_true",
        help="Overwrite src/main.cpp if it already exists.",
    )
    args = parser.parse_args()

    try:
        install_platformio()
        initialize_project()
        copy_source(force=args.force_copy)
        print_aircrack_instructions()
    except subprocess.CalledProcessError as exc:
        print(f"\nCommand failed with exit code {exc.returncode}.")
        return exc.returncode
    except Exception as exc:  # pragma: no cover - defensive setup error path
        print(f"\nSetup failed: {exc}")
        return 1

    print("\nSetup complete.")
    print("Next step: connect your ESP32 and run:")
    print("  python3 -m platformio run -t upload --upload-port <PORT>")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
