#!/usr/bin/env python3
"""Download a registered dataset (sample by default) to the external drive.

    python3 scripts/download-dataset.py --list
    python3 scripts/download-dataset.py taskmaster2 --dry-run
    python3 scripts/download-dataset.py taskmaster2            # sample subset
    python3 scripts/download-dataset.py taskmaster2 --full     # whole dataset

Sources come only from registry/datasets.json:
  url    - pinned raw files, fetched via a temp file on the drive, sha256 recorded
  hf     - Hugging Face dataset repo at a pinned revision (allow_patterns subset)
  manual - never fetched; instructions are printed (e.g. MDIS, BLS)

Same guard as download-model.py: no valid external root, no download.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import os
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dayos_storage as ds  # noqa: E402

REGISTRY = ds.REPO_ROOT / "registry" / "datasets.json"


def head_size(url: str) -> int:
    req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "dayos-storage/1"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return int(resp.headers.get("Content-Length") or 0)
    except Exception:  # noqa: BLE001 - size is advisory in the plan
        return 0


def plan_files(d: dict, section: dict) -> list[dict]:
    if d["source"] == "url":
        return [{"path": f["name"], "url": f["url"], "size": head_size(f["url"]), "sha256": f.get("sha256")}
                for f in section.get("files", [])]
    if d["source"] == "hf":
        pats = section.get("allow_patterns")
        exact = pats if pats and not any(c in p for p in pats for c in "*?[") else None
        files = ds.hf_repo_files(d["repo_id"], d.get("revision") or "main", repo_type="dataset",
                                 exact_paths=exact)
        return [f for f in files if not pats or any(fnmatch.fnmatch(f["path"], p) for p in pats)]
    return []


def fetch_url(url: str, dest: Path, tmp_dir: Path, attempts: int = 3) -> None:
    """Download to a temp file on the external drive, then move into place."""
    for attempt in range(1, attempts + 1):
        fd, tmp = tempfile.mkstemp(dir=tmp_dir, prefix=dest.name + ".")
        try:
            with os.fdopen(fd, "wb") as out, urllib.request.urlopen(
                urllib.request.Request(url, headers={"User-Agent": "dayos-storage/1"}), timeout=180
            ) as resp:
                while block := resp.read(1024 * 1024):
                    out.write(block)
            os.replace(tmp, dest)
            return
        except (TimeoutError, OSError) as exc:
            if attempt == attempts:
                raise
            print(f"  retry {attempt}/{attempts - 1} for {dest.name}: {exc}", file=sys.stderr)
            time.sleep(2 * attempt)
        finally:
            if os.path.exists(tmp):
                os.unlink(tmp)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("dataset", nargs="?")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--full", action="store_true", help="download the full dataset instead of the sample")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--yes", action="store_true")
    args = ap.parse_args()

    registry = json.loads(REGISTRY.read_text())["datasets"]
    if args.list or not args.dataset:
        print(f"{'key':18} {'source':7} {'sample GB':>9} {'full GB':>8}  license")
        for key, d in registry.items():
            print(f"{key:18} {d['source']:7} {d['sample'].get('approx_gb', 0):>9.3f} "
                  f"{d['full'].get('approx_gb', 0):>8.3f}  {d['license']}")
        return 0
    if args.dataset not in registry:
        print(f"unknown dataset '{args.dataset}'. Use --list.", file=sys.stderr)
        return 2
    d = registry[args.dataset]
    variant = "full" if args.full else "sample"
    section = d[variant]

    print(f"Dataset    : {args.dataset}  ({variant})")
    print(f"License    : {d['license']}  | commercial: {d.get('commercial_use', 'unverified')}")
    if d.get("_note"):
        print(f"Note       : {d['_note']}")
    if d["source"] == "manual":
        print(f"Manual     : {d['instructions']}")
        return 0
    if section.get("blocked"):
        print(f"[dayos] {variant} download is blocked for {args.dataset} (see registry note).")
        return 0 if args.dry_run else 3

    status = ds.validate_root(ds.load_env().get("DAYOS_ASSETS_ROOT"))
    if not status.ok and not args.dry_run:
        print(f"[dayos] STOP: external storage not ready: {status.reason}", file=sys.stderr)
        return 1

    files = plan_files(d, section)
    if not files:
        print("[dayos] No files configured for this variant yet (URL/revision must be pinned first).")
        return 0 if args.dry_run else 3
    total = sum(f["size"] for f in files)
    need = ds.required_bytes(total)
    dest = (status.root / "datasets" / "raw" / args.dataset / variant) if status.root else None
    print(f"Files      : {len(files)}  ({', '.join(f['path'] for f in files[:4])}{' …' if len(files) > 4 else ''})")
    print(f"Download   : {ds.fmt_gb(total)}   need free {ds.fmt_gb(need)}")
    print(f"Assets root: {status.root or '-'}  [{status.reason}]")
    if status.ok:
        print(f"External   : {ds.fmt_gb(ds.free_bytes(status.root))} free")
        print(f"Destination: {dest}")
    if args.dry_run:
        print("(dry run — nothing downloaded)")
        return 0

    if ds.free_bytes(status.root) < need:
        print("[dayos] STOP: not enough free space on the external drive.", file=sys.stderr)
        return 1
    if not args.yes and not ds.confirm(f"Download {ds.fmt_gb(total)} to {dest}?"):
        print("Aborted.")
        return 1

    ds.export_cache_env(status.root)
    dest.mkdir(parents=True, exist_ok=True)
    if d["source"] == "url":
        for f in files:
            fetch_url(f["url"], dest / f["path"], status.root / "tmp")
    else:
        from huggingface_hub import snapshot_download  # after env is set

        snapshot_download(repo_id=d["repo_id"], repo_type="dataset", revision=d.get("revision"),
                          local_dir=dest, allow_patterns=section.get("allow_patterns"))

    problems = []
    for f in files:
        p = dest / f["path"]
        if not p.is_file():
            problems.append(f"missing: {f['path']}")
            continue
        got = ds.sha256_file(p)
        if f.get("sha256") and got != f["sha256"]:
            problems.append(f"sha256 mismatch: {f['path']}")
        elif f.get("git_blob_sha1") and ds.git_blob_sha1(p) != f["git_blob_sha1"]:
            problems.append(f"git blob sha1 mismatch: {f['path']}")
        f["sha256_local"] = got
        f["size_local"] = p.stat().st_size
    manifest = {"dataset": args.dataset, "variant": variant, "license": d["license"], "files": files,
                "verified": not problems, "problems": problems,
                "downloaded_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    (dest / "DAYOS_MANIFEST.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False))
    (status.root / "manifests" / f"dataset-{args.dataset}-{variant}.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False))
    print("verify:", "OK" if not problems else "\n  ".join(["FAILED"] + problems))
    return 0 if not problems else 4


if __name__ == "__main__":
    sys.exit(main())
