# Official Curios migration, 2026-09-28

## Agreed scope

Update Curios from `17.0.0-beta+26.3` to official `17.0.0-beta.2+26.3`
(Modrinth `LeVAnMq4`), remove `aziran-backpack-curios-1.0.0.jar` entirely,
and build client pack 1.1.13. Keep Minecraft, NeoForge, Traveler's Backpack,
all other mods, configuration, resources, worlds and client defaults unchanged.
Retain historical compatibility source and deployment records, marked retired.

The official fix makes Curios getters return the stored ItemStack. The runtime
getter assertion now verifies this intentional upstream contract. Identical-bag
replacement fixtures explicitly copy the stack, since fetching it no longer
creates a distinct object. Expected replacement contents are separate snapshots.

## Explicit user decision

The isolated official-only run passed normal persistence but failed three
stale-menu guards previously supplied by the local addon. The coordinator
explained the difference and offered retaining only these protections or using
official mods alone. The user chose **자체 패치를 완전히 제거하고 공식판만 사용하기**.

Thus replacing a worn bag while its menu is open is an acknowledged upstream
limitation, not part of the selected official-only migration acceptance. Keep
the assertions and their failures visible; do not report a clean full runtime
suite or add a new local patch. Test current-wrapper lookup separately to
identify whether stale menus can also route writes to the old bag.

## Verification and deployment gates

1. Verify downloaded Curios bytes against official size and SHA-512.
2. Use `tests/backpack-runtime/run.py --curios <staged-jar> --full-modset`
   with disposable worlds and no production world/config mounts. Require
   ordinary menu persistence, removal/count changes, tools/upgrades/settings,
   constructor changes, Curios serialization/ticking, other contexts, and a
   separate server process reading persisted contents to pass. Report stale
   replacement failures separately; the full harness still exits nonzero.
3. Normal server shutdown and verified **world-only** backup following
   `docs/BACKUPS.md`, including all dimensions, before live mod changes.
4. Replace old Curios and remove addon, keep unrelated JAR hashes unchanged.
   Confirm healthy startup, expected mod versions, RCON, and no new load errors.
5. Build three client formats, run Python/JavaScript checks, compare archive
   payloads to 1.1.12, and independently verify official JAR and addon absence.
6. Commit/push and publish the new client release after review. Do not claim
   human client or singleplayer testing from server-side automated checks.

Final official runtime evidence: `/tmp/aziran-backpack-test-ytu9tcj3`:
14 passes across two server processes; 4 failures (`stale_replaced_bag`,
`stale_identical_bag`, `stale_settings_menu`,
`replacement_lookup_uses_current_bag`). The latter confirms a lookup can keep
the old menu wrapper after the worn bag is replaced. This is the same accepted
replacement edge case, not ordinary close/reopen persistence. Both Java
processes exited 0; the test runner correctly exited 1. Ordinary persistence
and the independent restart read passed. Production remains unchanged at this
checkpoint.

## Deployment and independent verification

- Production stopped normally at 03:43:57 UTC (`exit=0`, `oom=false`), with
  player saves, all three dimension saves and runner `Done` independently read
  from Docker logs.
- World-only archive:
  `/home/pilon1945/aziran-26.3-protected-backups/pre-curios-beta2-world-2026-09-28-034407.tar`.
  Independently reopened: 3,843 entries, 11,454,986,240 bytes, only paths under
  `server-data-26.3-neoforge/world/`, `level.dat` and all three dimension region
  paths present. Independently recomputed SHA-256:
  `5fa96ee1f764e773af73b130385732507b1a06968acf951afd97039e2b9e5fb4`.
- Same container started at 03:44:57 UTC; `Done` at 03:45:11, healthy and RCON
  responsive. Official Curios beta.2 loaded; old Curios and addon removed.
  The other 23 installed mod hashes match the prior baseline.
- Persistent configuration is unchanged. Spark rotated temporary profiler files.
  PacketFixer rewrote its generated timestamp: restoring only the old comment
  `#Sat Sep 26 12:20:44 KST 2026` reproduced its exact pre-deployment SHA-256.
- Existing Occultism integration/refmap/udev/data-map warnings remain. The
  `DebugFile` logging exception involving Netty `kqueue.Native` also appeared
  in older startup logs (including 2026-09-25); it is not newly introduced here.
- Codex independently ran all 66 Python tests and 2 JavaScript tests: passed.
  Earlier Python failures were stale 1.1.12 archive references, corrected by
  Codex to the agreed 1.1.13 delivery and mod counts, then rerun.
- All three 1.1.13 archive contents were compared to saved 1.1.12 entry hashes.
  Only Curios replacement/addon removal and generated metadata/docs changed.
  Other JARs, resources, config, options and server-list payloads are identical;
  other Modrinth download entries are unchanged. Bundled/downloaded Curios hashes
  match the independently downloaded official artifact. Release checksum file
  independently verified for every listed asset.

## Published release

`client-1.1.13` tags source commit `fae58ca`. All seven draft assets were
downloaded again and matched local bytes before publication at 2026-09-28
03:50:31 UTC as a normal release/latest. The `.mrpack` SHA-256 is
`851023c013181b112a417dd71926d41749172c44f9726cc2d9df65e3a159a38e`.
Final README wording was corrected to identify replacement, not removal, as
the failing edge case; rebuilt archive/config tests (5) and checksums passed.
