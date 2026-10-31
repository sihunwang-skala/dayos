# shellcheck shell=bash
# Shared helpers for DayOS external-storage scripts. Source, don't execute.
#
# Contract: every large artifact lives under $DAYOS_ASSETS_ROOT on an external
# volume. If that root is missing, unmounted, or on the internal disk, callers
# must stop instead of falling back to ~/.cache.

DAYOS_REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../.." && pwd)"
DAYOS_MARKER_NAME=".dayos-assets"

dayos_log()  { printf '[dayos] %s\n' "$*" >&2; }
dayos_die()  { printf '[dayos] ERROR: %s\n' "$*" >&2; exit 1; }

# Load DAYOS_* settings from the repo's .env (never exported globally).
dayos_load_env() {
  local env_file="$DAYOS_REPO_ROOT/.env"
  if [[ -f "$env_file" ]]; then
    # Only accept simple KEY=VALUE lines for DAYOS_* keys.
    while IFS='=' read -r key value; do
      [[ "$key" =~ ^DAYOS_[A-Z0-9_]+$ ]] || continue
      value="${value%\"}"; value="${value#\"}"
      export "$key=$value"
    done < <(grep -E '^DAYOS_[A-Z0-9_]+=' "$env_file")
  fi
}

# Print the mount point that contains PATH.
dayos_mount_point() { df -P "$1" 2>/dev/null | awk 'NR==2 {print $6}'; }

# Print the volume UUID for a mount point (empty if unknown).
dayos_volume_uuid() {
  diskutil info "$1" 2>/dev/null | awk -F': *' '/Volume UUID/ {print $2; exit}'
}

# Validate that ROOT is a usable external assets root. Returns non-zero with a
# message instead of exiting so callers can decide (check vs. hard stop).
dayos_validate_root() {
  local root="$1" require_marker="${2:-yes}"
  if [[ -z "$root" ]]; then
    dayos_log "DAYOS_ASSETS_ROOT is not set (run scripts/setup-external-storage.sh)."; return 1
  fi
  if [[ "$root" != /Volumes/* ]]; then
    dayos_log "DAYOS_ASSETS_ROOT must be under /Volumes/<external-drive>: $root"; return 1
  fi
  local vol_dir
  vol_dir="/Volumes/$(cut -d/ -f3 <<<"$root")"
  if [[ ! -d "$vol_dir" ]]; then
    dayos_log "Volume not mounted: $vol_dir"; return 1
  fi
  local mp
  mp="$(dayos_mount_point "$vol_dir")"
  if [[ "$mp" != "$vol_dir" ]]; then
    # A plain folder under /Volumes on the internal disk would pass -d; reject it.
    dayos_log "$vol_dir is not a mount point (resolves to '$mp'); refusing to use internal disk."; return 1
  fi
  if [[ "$(stat -f %d "$vol_dir")" == "$(stat -f %d "$HOME")" ]]; then
    dayos_log "$vol_dir is on the same device as \$HOME; refusing."; return 1
  fi
  if [[ "$require_marker" == "yes" ]]; then
    if [[ ! -f "$root/$DAYOS_MARKER_NAME" ]]; then
      dayos_log "Marker $root/$DAYOS_MARKER_NAME missing (wrong drive or setup not run)."; return 1
    fi
    local want have
    want="$(awk -F= '/^volume_uuid=/ {print $2}' "$root/$DAYOS_MARKER_NAME")"
    have="$(dayos_volume_uuid "$mp")"
    if [[ -n "$want" && -n "$have" && "$want" != "$have" ]]; then
      dayos_log "Volume UUID mismatch (marker=$want, mounted=$have)."; return 1
    fi
    if [[ ! -w "$root" ]]; then
      dayos_log "No write permission on $root"; return 1
    fi
  fi
  return 0
}

# Export cache/temp locations so tools write to the external drive.
# Verified against huggingface_hub 1.32.0 and Ollama 0.33.0 on 2026-10-31.
dayos_export_cache_env() {
  local root="$1"
  export HF_HOME="$root/cache/huggingface"
  export HF_HUB_CACHE="$root/cache/huggingface/hub"
  export HF_XET_CACHE="$root/cache/huggingface/xet"
  export HF_ASSETS_CACHE="$root/cache/huggingface/assets"
  # Keep the existing login token where it is (tiny file) instead of copying it.
  export HF_TOKEN_PATH="${HF_TOKEN_PATH:-$HOME/.cache/huggingface/token}"
  # transformers/datasets resolve their caches from HF_HOME / HF_HUB_CACHE.
  export TORCH_HOME="$root/cache/torch"
  export XDG_CACHE_HOME="$root/cache/xdg"
  export PIP_CACHE_DIR="$root/cache/pip"
  export UV_CACHE_DIR="$root/cache/uv"
  export OLLAMA_MODELS="$root/models/ollama"
  export TMPDIR="$root/tmp/"
  export DAYOS_ASSETS_ROOT="$root"
}
