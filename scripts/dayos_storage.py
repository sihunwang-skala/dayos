"""Shared storage guard for DayOS download scripts.

Python mirror of scripts/lib/storage-env.sh. The rule is the same: large
artifacts go under DAYOS_ASSETS_ROOT on an external volume, and if that root
is not valid we stop rather than fall back to the internal disk.

Standard library only, so dry runs work before any dependency is installed.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MARKER_NAME = ".dayos-assets"
GB = 1_000_000_000
# Extra headroom on top of the payload: partial files, metadata, filesystem slack.
SPACE_MARGIN_RATIO = 1.10
SPACE_MARGIN_FIXED = 5 * GB


def load_env() -> dict[str, str]:
    """Read DAYOS_* keys from the repo's .env without touching os.environ."""
    env: dict[str, str] = {}
    path = REPO_ROOT / ".env"
    if path.exists():
        for line in path.read_text().splitlines():
            key, sep, value = line.partition("=")
            if sep and key.startswith("DAYOS_"):
                env[key.strip()] = value.strip().strip('"')
    # An explicit environment variable wins over .env.
    if os.environ.get("DAYOS_ASSETS_ROOT"):
        env["DAYOS_ASSETS_ROOT"] = os.environ["DAYOS_ASSETS_ROOT"]
    return env


def _volume_uuid(mount: Path) -> str:
    try:
        out = subprocess.run(
            ["diskutil", "info", str(mount)], capture_output=True, text=True, check=False
        ).stdout
    except FileNotFoundError:
        return ""
    for line in out.splitlines():
        if "Volume UUID" in line:
            return line.split(":", 1)[1].strip()
    return ""


@dataclass
class RootStatus:
    root: Path | None
    ok: bool
    reason: str


def validate_root(root_str: str | None) -> RootStatus:
    if not root_str:
        return RootStatus(None, False, "DAYOS_ASSETS_ROOT is not set (run scripts/setup-external-storage.sh)")
    root = Path(root_str)
    parts = root.parts
    if len(parts) < 3 or parts[1] != "Volumes":
        return RootStatus(root, False, f"must be under /Volumes/<external-drive>: {root}")
    vol = Path("/Volumes") / parts[2]
    if not vol.is_dir():
        return RootStatus(root, False, f"volume not mounted: {vol}")
    if not os.path.ismount(vol):
        return RootStatus(root, False, f"{vol} is not a mount point; refusing to use internal disk")
    if os.stat(vol).st_dev == os.stat(Path.home()).st_dev:
        return RootStatus(root, False, f"{vol} is on the same device as $HOME")
    marker = root / MARKER_NAME
    if not marker.is_file():
        return RootStatus(root, False, f"marker {marker} missing (wrong drive or setup not run)")
    want = ""
    for line in marker.read_text().splitlines():
        if line.startswith("volume_uuid="):
            want = line.split("=", 1)[1].strip()
    have = _volume_uuid(vol)
    if want and have and want != have:
        return RootStatus(root, False, f"volume UUID mismatch (marker={want}, mounted={have})")
    if not os.access(root, os.W_OK):
        return RootStatus(root, False, f"no write permission on {root}")
    return RootStatus(root, True, "ready")


def export_cache_env(root: Path) -> None:
    """Point every cache/temp location at the external root.

    Must run before importing huggingface_hub / transformers / torch, because
    those read their cache paths at import time.
    """
    hf = root / "cache" / "huggingface"
    os.environ.update(
        {
            "DAYOS_ASSETS_ROOT": str(root),
            "HF_HOME": str(hf),
            "HF_HUB_CACHE": str(hf / "hub"),
            "HF_XET_CACHE": str(hf / "xet"),
            "HF_ASSETS_CACHE": str(hf / "assets"),
            "TORCH_HOME": str(root / "cache" / "torch"),
            "XDG_CACHE_HOME": str(root / "cache" / "xdg"),
            "PIP_CACHE_DIR": str(root / "cache" / "pip"),
            "UV_CACHE_DIR": str(root / "cache" / "uv"),
            "OLLAMA_MODELS": str(root / "models" / "ollama"),
            "TMPDIR": str(root / "tmp") + "/",
        }
    )
    # Keep using the existing login token instead of copying it to the drive.
    os.environ.setdefault("HF_TOKEN_PATH", str(Path.home() / ".cache" / "huggingface" / "token"))
    import tempfile

    tempfile.tempdir = None  # re-read TMPDIR


def free_bytes(path: Path) -> int:
    return shutil.disk_usage(path).free


def required_bytes(payload: int) -> int:
    return int(payload * SPACE_MARGIN_RATIO) + SPACE_MARGIN_FIXED


def dir_size(path: Path) -> int:
    total = 0
    if not path.exists():
        return 0
    for dirpath, _dirnames, filenames in os.walk(path):
        for name in filenames:
            p = os.path.join(dirpath, name)
            if not os.path.islink(p):
                try:
                    total += os.path.getsize(p)
                except OSError:
                    pass
    return total


def sha256_file(path: Path, chunk: int = 8 * 1024 * 1024) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while block := f.read(chunk):
            h.update(block)
    return h.hexdigest()


def _hf_request(url: str, data: bytes | None = None) -> urllib.request.Request:
    req = urllib.request.Request(url, data=data, headers={"User-Agent": "dayos-storage/1"})
    token_path = Path(os.environ.get("HF_TOKEN_PATH", Path.home() / ".cache/huggingface/token"))
    if token_path.is_file():
        req.add_header("Authorization", f"Bearer {token_path.read_text().strip()}")
    return req


def hf_repo_files(
    repo_id: str, revision: str, repo_type: str = "model", exact_paths: list[str] | None = None
) -> list[dict]:
    """List files with size and hashes via the public Hub API (no cache writes).

    With exact_paths, only those paths are queried (paths-info), which keeps
    repos with very many files (e.g. 100k+ screenshots) fast.
    """
    kind = {"model": "models", "dataset": "datasets"}[repo_type]
    if exact_paths:
        body = urllib.parse.urlencode([("paths", p) for p in exact_paths] + [("expand", "true")]).encode()
        url = f"https://huggingface.co/api/{kind}/{repo_id}/paths-info/{revision}"
        with urllib.request.urlopen(_hf_request(url, body), timeout=60) as resp:
            entries = json.load(resp)
        return [
            {
                "path": e["path"],
                "size": e.get("size") or 0,
                "sha256": (e.get("lfs") or {}).get("oid"),
                "git_blob_sha1": None if e.get("lfs") else e.get("oid"),
            }
            for e in entries
            if e.get("type") == "file"
        ]
    url = f"https://huggingface.co/api/{kind}/{repo_id}/revision/{revision}?blobs=true"
    with urllib.request.urlopen(_hf_request(url), timeout=120) as resp:
        info = json.load(resp)
    files = []
    for s in info.get("siblings", []):
        lfs = s.get("lfs") or {}
        files.append({
            "path": s["rfilename"],
            "size": s.get("size") or 0,
            "sha256": lfs.get("sha256"),
            # For non-LFS files the Hub reports the git blob id (sha1 of "blob <size>\0" + content).
            "git_blob_sha1": None if lfs else s.get("blobId"),
        })
    return files


def git_blob_sha1(path: Path) -> str:
    h = hashlib.sha1()
    h.update(f"blob {path.stat().st_size}\0".encode())
    with open(path, "rb") as f:
        while block := f.read(1024 * 1024):
            h.update(block)
    return h.hexdigest()


def fmt_gb(n: int | float) -> str:
    return f"{n / GB:,.2f} GB"


def confirm(prompt: str) -> bool:
    if not sys.stdin.isatty():
        return False
    return input(f"{prompt} [y/N] ").strip().lower() == "y"
