#!/usr/bin/env bash
# Prepare the DayOS asset tree on an external drive.
#
#   scripts/setup-external-storage.sh --volume /Volumes/<NAME> [--subdir dayos-assets] [--dry-run] [--yes]
#
# The volume path is never guessed: without --volume this only lists candidates.
# Nothing is written until the report has been shown and confirmed.
set -euo pipefail
source "$(dirname "$0")/lib/storage-env.sh"

VOLUME="" SUBDIR="dayos-assets" DRY_RUN=0 ASSUME_YES=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --volume) VOLUME="${2:-}"; shift 2 ;;
    --subdir) SUBDIR="${2:-}"; shift 2 ;;
    --dry-run) DRY_RUN=1; shift ;;
    --yes) ASSUME_YES=1; shift ;;
    -h|--help) sed -n '2,8p' "$0"; exit 0 ;;
    *) dayos_die "Unknown argument: $1" ;;
  esac
done

list_candidates() {
  echo "Mounted volumes under /Volumes (excluding the boot volume):"
  local found=0 v mp
  for v in /Volumes/*; do
    [[ -d "$v" ]] || continue
    mp="$(dayos_mount_point "$v")"
    [[ "$mp" == "$v" ]] || continue
    [[ "$(stat -f %d "$v")" == "$(stat -f %d "$HOME")" ]] && continue
    found=1
    printf '  %s  (%s)\n' "$v" "$(diskutil info "$v" 2>/dev/null | awk -F': *' '/File System Personality/ {print $2}')"
  done
  [[ $found -eq 1 ]] || echo "  (none — connect the external drive first)"
}

if [[ -z "$VOLUME" ]]; then
  list_candidates
  echo
  echo "Re-run with --volume /Volumes/<NAME> after confirming the path."
  exit 2
fi

VOLUME="${VOLUME%/}"
ROOT="$VOLUME/$SUBDIR"
dayos_validate_root "$ROOT" no || exit 1

info="$(diskutil info "$VOLUME")"
field() { awk -F': *' -v k="$1" '$1 ~ "^ *"k"$" {print $2; exit}' <<<"$info"; }
FS="$(field 'File System Personality')"
LOCATION="$(field 'Device Location')"
INTERNAL="$(field 'Internal')"
UUID="$(field 'Volume UUID')"
read -r TOTAL_K FREE_K < <(df -k "$VOLUME" | awk 'NR==2 {print $2, $4}')
INT_FREE_K="$(df -k "$HOME" | awk 'NR==2 {print $4}')"

WRITE_OK=no SYMLINK_OK=no
probe="$VOLUME/.dayos-write-probe.$$"
if touch "$probe" 2>/dev/null; then
  WRITE_OK=yes
  ln -s "$probe" "$probe.lnk" 2>/dev/null && SYMLINK_OK=yes
  rm -f "$probe" "$probe.lnk"
fi

gb() { awk -v k="$1" 'BEGIN {printf "%.1f GB", k*1024/1e9}'; }
cat <<EOF
External storage report
  Mount path        : $VOLUME
  Assets root       : $ROOT
  File system       : ${FS:-unknown}
  Device location   : ${LOCATION:-unknown} (Internal: ${INTERNAL:-unknown})
  Volume UUID       : ${UUID:-unknown}
  Capacity / free   : $(gb "$TOTAL_K") / $(gb "$FREE_K")
  Writable          : $WRITE_OK
  Symlinks          : $SYMLINK_OK
  Internal disk free: $(gb "$INT_FREE_K")
EOF

case "$FS" in
  *FAT32*|*MS-DOS*) dayos_die "FAT32 cannot store files >4GB (model shards are larger). Reformat as APFS or exFAT." ;;
  *ExFAT*|*exFAT*) dayos_log "WARNING: exFAT has no symlinks/permissions; HF cache will copy instead of link and macOS writes ._ files. APFS is preferred." ;;
esac
[[ "$INTERNAL" == "Yes" ]] && dayos_die "diskutil reports this volume as internal; refusing."
if [[ "$(field 'Protocol')" == "Disk Image" ]]; then
  dayos_log "WARNING: this volume is a mounted disk image; its backing file may live on the internal disk."
fi
[[ "$WRITE_OK" == "yes" ]] || dayos_die "Volume is not writable."

DIRS=(
  models/skt models/other models/ollama
  datasets/raw datasets/processed
  cache/huggingface/hub cache/huggingface/xet cache/huggingface/assets
  cache/transformers cache/torch cache/pip cache/uv cache/xdg
  tmp checkpoints experiments logs manifests
)

echo
echo "Will create under $ROOT:"
printf '  %s/\n' "${DIRS[@]}"
echo "Will write $ROOT/$DAYOS_MARKER_NAME and set DAYOS_ASSETS_ROOT in $DAYOS_REPO_ROOT/.env"

if [[ $DRY_RUN -eq 1 ]]; then echo "(dry run — nothing written)"; exit 0; fi
if [[ $ASSUME_YES -ne 1 ]]; then
  read -r -p "Proceed? [y/N] " ans
  [[ "$ans" == "y" || "$ans" == "Y" ]] || { echo "Aborted."; exit 1; }
fi

for d in "${DIRS[@]}"; do mkdir -p "$ROOT/$d"; done
cat > "$ROOT/$DAYOS_MARKER_NAME" <<EOF
# DayOS assets root marker. Scripts refuse to write unless this file matches.
volume_uuid=$UUID
created=$(date -u +%Y-%m-%dT%H:%M:%SZ)
EOF

env_file="$DAYOS_REPO_ROOT/.env"
touch "$env_file"
if grep -q '^DAYOS_ASSETS_ROOT=' "$env_file"; then
  tmp="$(mktemp "$ROOT/tmp/env.XXXXXX")"
  sed "s|^DAYOS_ASSETS_ROOT=.*|DAYOS_ASSETS_ROOT=$ROOT|" "$env_file" > "$tmp" && mv "$tmp" "$env_file"
else
  echo "DAYOS_ASSETS_ROOT=$ROOT" >> "$env_file"
fi
dayos_log "Done. Run scripts/check-storage.sh to verify."
