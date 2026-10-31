# shellcheck shell=bash
# Source this in a terminal to point HF/torch/pip/Ollama caches at the external
# drive for the current shell only:
#
#   source scripts/dayos-env.sh && ollama serve
#
# Refuses (and leaves the shell unchanged) if the drive is not ready.
_dayos_env_main() {
  local here
  here="$(cd "$(dirname "${BASH_SOURCE[0]:-${(%):-%x}}")" && pwd)"
  # Run validation in a subshell so dayos_die can't kill the caller's shell.
  if ! bash -c "source '$here/lib/storage-env.sh'; dayos_load_env; dayos_validate_root \"\${DAYOS_ASSETS_ROOT:-}\" yes"; then
    echo "[dayos] environment NOT changed." >&2
    return 1
  fi
  local root
  root="$(grep -E '^DAYOS_ASSETS_ROOT=' "$here/../.env" | tail -1 | cut -d= -f2-)"
  root="${root%\"}"; root="${root#\"}"
  # shellcheck source=lib/storage-env.sh
  source "$here/lib/storage-env.sh"
  dayos_export_cache_env "$root"
  echo "[dayos] caches -> $root" >&2
}
_dayos_env_main
