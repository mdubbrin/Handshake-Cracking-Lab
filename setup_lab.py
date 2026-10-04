#!/usr/bin/env python3
"""Cross-platform setup helper for the Handshake Cracking Lab."""

from __future__ import annotations

import argparse
import platform
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent
SRC_DIR = REPO_ROOT / "src"
SRC_MAIN_CPP = SRC_DIR / "main.cpp"
PLATFORMIO_INI = REPO_ROOT / "platformio.ini"
INCLUDE_DIR = REPO_ROOT / "include"
LIB_DIR = REPO_ROOT / "lib"


def run(cmd: list[str], *, check: bool = True) -> subprocess.CompletedProcess:
    print("\n$", " ".join(cmd))
    return subprocess.run(cmd, check=check)


def install_platformio() -> None:
    print("Installing/Updating PlatformIO Core...")
    run([sys.executable, "-m", "pip", "install", "--user", "platformio"])


def verify_project_layout() -> None:
    missing_paths: list[Path] = []
    for path in (PLATFORMIO_INI, SRC_DIR, SRC_MAIN_CPP, INCLUDE_DIR, LIB_DIR):
        if not path.exists():
            missing_paths.append(path)

    if missing_paths:
        missing = "\n".join(f"- {path.relative_to(REPO_ROOT)}" for path in missing_paths)
        raise FileNotFoundError(
            "Expected PlatformIO project files are missing. Restore these paths:\n"
            f"{missing}"
        )

    print("PlatformIO project files are present in the repository.")


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
    parser.parse_args()

    try:
        install_platformio()
        verify_project_layout()
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
