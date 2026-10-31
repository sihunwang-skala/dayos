#!/usr/bin/env bash
# Report DayOS storage health: external assets root, internal disk headroom,
# and caches that are still accumulating on the internal disk.
#
#   scripts/check-storage.sh [--quiet]
#
# Exit codes: 0 = external root valid, 1 = invalid/not connected.
set -uo pipefail
source "$(dirname "$0")/lib/storage-env.sh"
dayos_load_env

QUIET=0
[[ "${1:-}" == "--quiet" ]] && QUIET=1
say() { [[ $QUIET -eq 1 ]] || echo "$@"; }

gb() { awk -v k="$1" 'BEGIN {printf "%.1f GB", k*1024/1e9}'; }

say "== Internal disk"
read -r int_total int_free < <(df -k "$HOME" | awk 'NR==2 {print $2, $4}')
say "  free $(gb "$int_free") of $(gb "$int_total")"
if (( int_free < 20*1024*1024 )); then
  say "  WARNING: less than 20GB free on the internal disk."
fi

say "== Caches on the internal disk (not touched by this script)"
for p in "$HOME/.cache/huggingface" "$HOME/.ollama/models" "$HOME/.cache/torch" \
         "$HOME/Library/Caches/pip" "$HOME/.cache/uv" "$HOME/.cache/pip"; do
  [[ -e "$p" ]] && say "  $(du -sh "$p" 2>/dev/null | cut -f1)	$p"
done

say "== External assets root"
ROOT="${DAYOS_ASSETS_ROOT:-}"
say "  DAYOS_ASSETS_ROOT=${ROOT:-<unset>}"
if ! dayos_validate_root "$ROOT" yes; then
  say "  status: NOT READY — downloads are disabled."
  exit 1
fi
mp="$(dayos_mount_point "$ROOT")"
read -r ext_total ext_free < <(df -k "$ROOT" | awk 'NR==2 {print $2, $4}')
fs="$(diskutil info "$mp" | awk -F': *' '/File System Personality/ {print $2}')"
say "  mount $mp  fs ${fs:-unknown}  free $(gb "$ext_free") of $(gb "$ext_total")"
for d in models datasets cache checkpoints experiments tmp; do
  [[ -d "$ROOT/$d" ]] && say "  $(du -sh "$ROOT/$d" 2>/dev/null | cut -f1)	$d/"
done

say "== Effective env inside DayOS scripts"
dayos_export_cache_env "$ROOT"
for v in HF_HOME HF_HUB_CACHE HF_XET_CACHE TORCH_HOME XDG_CACHE_HOME PIP_CACHE_DIR UV_CACHE_DIR OLLAMA_MODELS TMPDIR; do
  say "  $v=${!v}"
done
say "  status: READY"
