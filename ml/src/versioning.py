"""Helpers to make every training run traceable to a Git commit + DVC data version.

Reads the `.dvc` pointer file directly (it stores the MD5 hash DVC uses to
address the data in remote storage) instead of shelling out to `dvc`, so
this works even where the `dvc` CLI isn't installed.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import yaml


def get_git_commit(short: bool = False) -> str:
    try:
        args = ["git", "rev-parse", "--short", "HEAD"] if short else ["git", "rev-parse", "HEAD"]
        return subprocess.check_output(args, stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return "unknown"


def get_dvc_data_version(dvc_file: Path) -> str:
    """Return the MD5 hash DVC recorded for the tracked dataset."""
    if dvc_file.exists():
        content = yaml.safe_load(dvc_file.read_text())
        outs = content.get("outs", [])
        if outs:
            return outs[0].get("md5", "unknown")
    return "no-dvc-file-yet"
