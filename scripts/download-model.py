#!/usr/bin/env python3
"""Download one registered model to the external drive, with checks.

    python3 scripts/download-model.py --list
    python3 scripts/download-model.py ax-4.0-light --dry-run
    python3 scripts/download-model.py ax-4.0-light            # asks for confirmation

Models come only from registry/models.json (pinned revision). The script:
  * refuses to run (except --dry-run / --list) unless DAYOS_ASSETS_ROOT is a
    valid external root, and never falls back to ~/.cache;
  * checks free space against the measured download size plus headroom;
  * points HF/xet/tmp caches at the drive before importing huggingface_hub;
  * verifies size and LFS sha256 of every file afterwards and writes a manifest.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dayos_storage as ds  # noqa: E402

REGISTRY = ds.REPO_ROOT / "registry" / "models.json"
LARGE_THRESHOLD = 100 * ds.GB


def load_registry() -> dict:
    return json.loads(REGISTRY.read_text())["models"]


def select_files(files: list[dict], patterns: list[str] | None) -> list[dict]:
    if not patterns:
        return files
    return [f for f in files if any(fnmatch.fnmatch(f["path"], p) for p in patterns)]


def verify(local_dir: Path, files: list[dict]) -> list[str]:
    problems = []
    for f in files:
        p = local_dir / f["path"]
        if not p.is_file():
            problems.append(f"missing: {f['path']}")
            continue
        size = p.stat().st_size
        if f["size"] and size != f["size"]:
            problems.append(f"size mismatch: {f['path']} ({size} != {f['size']})")
            continue
        if f["sha256"]:
            if ds.sha256_file(p) != f["sha256"]:
                problems.append(f"sha256 mismatch: {f['path']}")
                continue
        elif f.get("git_blob_sha1"):
            if ds.git_blob_sha1(p) != f["git_blob_sha1"]:
                problems.append(f"git blob sha1 mismatch: {f['path']}")
                continue
        print(f"  ok  {f['path']}")
    return problems


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("model", nargs="?", help="registry key, e.g. ax-4.0-light")
    ap.add_argument("--list", action="store_true", help="list registered models")
    ap.add_argument("--dry-run", action="store_true", help="show plan and checks; download nothing")
    ap.add_argument("--yes", action="store_true", help="skip the confirmation prompt")
    ap.add_argument("--allow-large", action="store_true", help=f"permit models over {LARGE_THRESHOLD // ds.GB} GB")
    ap.add_argument("--verify-only", action="store_true", help="re-verify an existing download")
    args = ap.parse_args()

    registry = load_registry()
    if args.list or not args.model:
        print(f"{'key':26} {'GB':>8}  {'status':20} repo")
        for key, m in registry.items():
            print(f"{key:26} {m['download_gb']:>8.1f}  {m['status']:20} {m['repo_id']}@{m['revision'][:10]}")
        return 0

    if args.model not in registry:
        print(f"unknown model '{args.model}'. Use --list.", file=sys.stderr)
        return 2
    m = registry[args.model]
    repo_id, revision = m["repo_id"], m["revision"]

    status = ds.validate_root(ds.load_env().get("DAYOS_ASSETS_ROOT"))
    if not status.ok and not args.dry_run:
        print(f"[dayos] STOP: external storage not ready: {status.reason}", file=sys.stderr)
        return 1

    files = select_files(ds.hf_repo_files(repo_id, revision), m.get("allow_patterns"))
    total = sum(f["size"] for f in files)
    need = ds.required_bytes(total)
    name = repo_id.split("/", 1)[1]
    local_dir = (status.root / "models" / m["subdir"] / name / revision[:12]) if status.root else None

    print(f"Model      : {repo_id}")
    print(f"Revision   : {revision}")
    print(f"Official   : {m['official']}   License: {m['license']}")
    print(f"Runs on Mac: {m['local_feasible']}")
    print(f"Files      : {len(files)}  ({fmt_list(files)})")
    print(f"Download   : {ds.fmt_gb(total)}  (registry says {m['download_gb']} GB)")
    print(f"Need free  : {ds.fmt_gb(need)} incl. headroom")
    print(f"Internal   : {ds.fmt_gb(ds.free_bytes(Path.home()))} free (should not change)")
    print(f"Assets root: {status.root or '-'}  [{status.reason}]")
    if status.ok:
        free = ds.free_bytes(status.root)
        print(f"External   : {ds.fmt_gb(free)} free -> {'OK' if free >= need else 'INSUFFICIENT'}")
        print(f"Destination: {local_dir}")

    blocked = m["status"] == "blocked-large" or total > LARGE_THRESHOLD
    if blocked and not args.allow_large:
        print(f"[dayos] {args.model} is {ds.fmt_gb(total)}; requires explicit --allow-large and user approval.")
        return 0 if args.dry_run else 3

    if args.dry_run:
        print("(dry run — nothing downloaded)")
        return 0

    if args.verify_only:
        problems = verify(local_dir, files)
        print("verify:", "OK" if not problems else "\n  ".join(["FAILED"] + problems))
        return 0 if not problems else 4

    if ds.free_bytes(status.root) < need:
        print("[dayos] STOP: not enough free space on the external drive.", file=sys.stderr)
        return 1
    if not args.yes and not ds.confirm(f"Download {ds.fmt_gb(total)} to {local_dir}?"):
        print("Aborted.")
        return 1

    ds.export_cache_env(status.root)
    internal_hf_before = ds.dir_size(Path.home() / ".cache" / "huggingface")
    from huggingface_hub import snapshot_download  # imported after env is set

    started = time.time()
    snapshot_download(
        repo_id=repo_id,
        revision=revision,
        local_dir=local_dir,
        allow_patterns=m.get("allow_patterns"),
    )
    print(f"downloaded in {time.time() - started:,.0f}s; verifying…")
    problems = verify(local_dir, files)

    # Re-validate: if the drive vanished mid-run we want to know.
    still = ds.validate_root(str(status.root))
    leak = ds.dir_size(Path.home() / ".cache" / "huggingface") - internal_hf_before
    manifest = {
        "model": args.model,
        "repo_id": repo_id,
        "revision": revision,
        "local_dir": str(local_dir),
        "files": files,
        "total_bytes": total,
        "verified": not problems,
        "problems": problems,
        "internal_hf_cache_growth_bytes": leak,
        "downloaded_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    (local_dir / "DAYOS_MANIFEST.json").write_text(json.dumps(manifest, indent=2))
    (status.root / "manifests" / f"model-{args.model}-{revision[:12]}.json").write_text(json.dumps(manifest, indent=2))

    if leak > 50_000_000:
        print(f"[dayos] WARNING: ~/.cache/huggingface grew by {ds.fmt_gb(leak)} during download.")
    if not still.ok:
        print(f"[dayos] WARNING: storage became invalid during download: {still.reason}")
    print("verify:", "OK" if not problems else "\n  ".join(["FAILED"] + problems))
    return 0 if not problems else 4


def fmt_list(files: list[dict], limit: int = 3) -> str:
    names = [f["path"] for f in files]
    return ", ".join(names[:limit]) + (f", … +{len(names) - limit}" if len(names) > limit else "")


if __name__ == "__main__":
    sys.exit(main())
