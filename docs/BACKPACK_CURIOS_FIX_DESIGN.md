# Curios Back-slot persistence patch: design and verification

Status: implemented, independently verified, and deployed on 2026-09-26.

## Requirement

Restore Traveler's Backpack's documented Curios Back-slot integration for the
installed Minecraft 26.3 / NeoForge 26.3.0.8-beta / Traveler's Backpack 11.4.0 /
Curios 17.0.0-beta+26.3 combination. Disabling integration is a temporary
mitigation, not the desired final behavior. Upstream report:
https://github.com/Tiviacz1337/Travelers-Backpack/issues/1618.

The installed Curios API returns detached ItemStacks. Backpack changes must
reach the owning Curios inventory. Do not
change the global Curios getter contract. Prefer a small server compatibility
mod over rebuilding unavailable exact-version upstream sources, provided all
affected mutation paths and server-only compatibility can be verified.

## Scope and constraints

- Pin supported dependency versions and make incompatible versions fail clearly.
- Cover storage, tools, upgrades, component changes, initial upgrade consumption,
  and passive ticking. Audit mutations outside BackpackWrapper as well.
- Preserve current Curios contents when a wrapper is stale or its bag was moved
  or replaced. Never overwrite another item with an old backpack snapshot.
- Keep native, held, and placed backpack behavior intact.
- Keep original upstream jars, player data formats, and network protocols where
  feasible. Do not restore the previously lost items or edit player NBT.
- Codex owns tests and verification; Claude owns production implementation.
- Deployment requires a normal shutdown and verified world-only backup under
  docs/BACKUPS.md. Existing native-worn bags must remain retrievable.

## Verification defined before implementation

Use the actual installed mod versions in an isolated temporary server world.
Test-only classes and resources must be excluded from the shipped artifact.
An automated server-side harness can verify the APIs and mixins; it does not
prove human client rendering, mouse interaction, or networking compatibility.

1. **Baseline failure:** equip a backpack in a real Curios Back handler, open a
   worn BackpackItemMenu, insert two iron nuggets, remove the menu, open a new
   menu, and assert exactly two nuggets remain. The original jars must fail
   this assertion with integration enabled; the patched setup must pass.
2. **Durable data:** serialize the Curios inventory containing identifiable
   contents, discard the player/wrapper, deserialize into a fresh player, and
   reopen. Compare items, counts, and relevant components. Where practical,
   repeat across separate server processes using a test fixture file.
3. **Mutation coverage:** storage removal/count changes, a valid tool slot,
   an upgrade slot, a backpack setting, starter-upgrade consumption, and a
   passive ticking path must be reflected in a fresh Curios read.
4. **Menu reuse:** mutate through the open menu and obtain the wrapper again
   through the normal worn lookup. Contents must not revert or duplicate.
5. **Stale ownership:** replace/remove the Curios item while retaining the old
   wrapper. The old wrapper must not overwrite the replacement or recreate
   the removed bag. Exercise the normal menu validity checks.
6. **Other contexts:** exercise a held wrapper and native attachment; neither
   may write into the Curios slot. Verify placed-wrapper save callbacks remain
   intact if the selected hook affects them.
7. **Packaging/deployment:** verify version pins, artifact contents and hashes,
   server startup with the full mod set, integration enabled only with the
   tested patch installed, and the existing Python/JavaScript checks.

After deployment, separately record actual player close/reopen and reconnect
confirmation. Do not equate startup success with those checks. Record any
unverified death/tomb, client, or upgrade cases explicitly.

## Architecture decision and results

Decision (2026-09-26): restore live references only at Traveler's Backpack's
two server entry points: `AttachmentUtils.getWearingBackpack` and the stack
passed by `TravelersBackpackCurio.curioTick` to `BackpackWrapper.tick`. A narrow
accessor to the Curios handler's actual stored stack supplies that reference.
Curios' public getters continue returning copies. Its own serialization then
sees the changed stack, as do its per-tick content comparisons for sync.

This revises the initial explicit-writeback proposal: attaching save callbacks
alone misses constructor changes and direct tick/ability changes, and detached
copies can conflict with an open menu's wrapper. The live reference covers all
audited mutation paths. Menu validity and wrapper reuse must check reference
identity so moving/replacing a slot cannot reuse the previous bag's wrapper.

The accessor uses private implementation details and bypasses the transfer
handler's mutation/journaling API. The inspected Curios handler has no content
change callback, and the inspected Traveler's Backpack operations do not run
inside transfer transactions. This is therefore an exact-version compatibility
patch, not a general replacement for the Curios resource API. All four mod/game
versions must be pinned; future updates require fresh review and runtime tests.

Codex's initial actual-server baseline completed at 2026-09-26 03:05 UTC.
`python3 tests/backpack-runtime/run.py` compiled a separate test-only mod using
Java 25 and the installed server libraries. A Docker container with no network
and no production world/config mounts started the exact NeoForge version with
only Traveler's Backpack, Curios, and the test mod in a fresh temporary world.

Five assertions failed: close/reopen (two iron nuggets became empty), Curios
inventory serialization (three diamonds became empty), tool persistence,
starter-upgrade consumption, and persistence after an open-menu setting update.
Two controls passed: Curios getters remained detached and held-backpack writes
left the Curios inventory unchanged. The server shut down normally with exit 0;
the test runner returned 1 because the regression assertions failed. Artifacts:
`/tmp/aziran-backpack-test-afijv7gr/`.

Final baseline (16 cases): 10 failures and 6 passes, including new stale-menu
and Curios tick synchronization checks (`/tmp/aziran-backpack-test-sv0nz8s9/`).
The patched full-modset run passed all 16 cases and a separate server-process
read of the serialized Curios inventory (`/tmp/aziran-backpack-test-3d6roffn/`).
Both server processes exited 0; the runner exited 0. These are real server APIs
with FakePlayers, not human client interaction or a full player-file reconnect.
The production jar excludes all test classes. Operational deployment details
and the independent world archive verification are in BACKPACK_PERSISTENCE.md.
After deployment the user confirmed reconnecting with their existing client,
equipping the bag in Curios Back, and retaining contents after close/reopen.
A read-only live entity query also showed the backpack storage component in
the serialized Curios inventory. A further human reconnect after insertion,
death/tomb behavior, and every individual upgrade remain unverified.
