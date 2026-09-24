#!/bin/bash
# Hourly backup of the 26.3 NeoForge world (all dimensions).
# Saving is paused with RCON while the archive is written and is always
# re-enabled on exit once it has been turned off.

set -Eeuo pipefail
umask 027

WORLD_DIR="${MC_BACKUP_WORLD_DIR:-/home/pilon1945/AziranMinecraftServer/server-data-26.3-neoforge/world}"
BACKUP_DIR="${MC_BACKUP_DIR:-/home/pilon1945/AziranMinecraftServer/minecraft_backups}"
CONTAINER="aziran-minecraft-26-3"
ARCHIVE_PREFIX="26.3-world-"
RETENTION_MINUTES=710

log() { printf '%s mc_backup: %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*"; }
fail() { log "ERROR: $*" >&2; exit 1; }

saving_off=0
partial=""

rcon() {
  docker exec "$CONTAINER" rcon-cli "$@"
}

# Re-enable saving; clears the recovery flag only when save-on succeeds.
restore_saving() {
  if rcon save-on; then
    saving_off=0
    log "saving re-enabled"
  else
    log "ERROR: save-on failed; world saving may still be disabled on $CONTAINER" >&2
    return 1
  fi
}

cleanup() {
  local status=$?
  trap - EXIT INT TERM HUP
  if [[ -n "$partial" && -e "$partial" ]]; then
    rm -f -- "$partial" || { log "ERROR: could not remove temporary archive $partial" >&2; status=1; }
  fi
  if (( saving_off )); then
    restore_saving || { (( status == 0 )) && status=1; }
  fi
  if (( status == 0 )); then
    log "backup finished"
  else
    log "backup FAILED (exit $status)" >&2
  fi
  exit "$status"
}
trap cleanup EXIT
trap 'log "interrupted by signal" >&2; exit 130' INT
trap 'log "terminated by signal" >&2; exit 143' TERM HUP

# Validate paths before touching the server.
[[ -d "$WORLD_DIR" ]] || fail "world directory not found: $WORLD_DIR"
[[ -n "$(find "$WORLD_DIR" -mindepth 1 -print -quit)" ]] || fail "world directory is empty: $WORLD_DIR"
[[ -f "$WORLD_DIR/level.dat" ]] || fail "world has no level.dat: $WORLD_DIR"
[[ -d "$BACKUP_DIR" && -w "$BACKUP_DIR" && -x "$BACKUP_DIR" ]] || fail "backup directory is not usable: $BACKUP_DIR"

# Prevent overlapping runs; the lock is held on this script for the process lifetime.
exec 9<"${BASH_SOURCE[0]}" || fail "cannot open lock on ${BASH_SOURCE[0]}"
flock -n 9 || fail "another backup is already running"

world_parent="$(cd "$(dirname "$WORLD_DIR")" && pwd)"
world_name="$(basename "$WORLD_DIR")"

log "disabling saving on $CONTAINER"
# Set the recovery flag first: save-off may take effect even if the CLI fails.
saving_off=1
rcon save-off || fail "save-off failed (container or RCON unreachable?)"
rcon save-all flush || fail "save-all flush failed"

partial="$(mktemp "$BACKUP_DIR/.${ARCHIVE_PREFIX}XXXXXX.partial")" || fail "cannot create temporary archive in $BACKUP_DIR"
log "writing $partial"
tar -cf "$partial" -C "$world_parent" "$world_name" || fail "tar failed"

# Keep the save-off window to the copy itself.
restore_saving || fail "save-on failed after archiving; not keeping or pruning archives"

# Verify the archive lists and can read level.dat.
listing="$(tar -tf "$partial")" || fail "verification failed: cannot list archive"
grep -qxF "$world_name/level.dat" <<<"$listing" || fail "verification failed: $world_name/level.dat missing from archive"
tar -xOf "$partial" "$world_name/level.dat" > /dev/null || fail "verification failed: cannot read $world_name/level.dat from archive"

chmod 0640 "$partial" || fail "cannot set archive permissions"
final="$BACKUP_DIR/${ARCHIVE_PREFIX}$(date '+%Y%m%d-%H%M%S').tar"
[[ ! -e "$final" ]] || fail "archive already exists: $final"
mv -T -- "$partial" "$final" || fail "cannot rename archive to $final"
partial=""
log "created $final"

find "$BACKUP_DIR" -maxdepth 1 -type f -name "${ARCHIVE_PREFIX}*.tar" -mmin +"$RETENTION_MINUTES" -print -delete \
  || fail "pruning old archives failed"
