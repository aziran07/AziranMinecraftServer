# Aziran Backpack Curios Persistence

A server-only compatibility mod that makes the Traveler's Backpack Curios Back slot persist its contents again.
It supports exactly Minecraft 26.3, NeoForge 26.3.0.8-beta, Traveler's Backpack 11.4.0, and Curios 17.0.0-beta+26.3.
Design and acceptance criteria: [docs/BACKPACK_CURIOS_FIX_DESIGN.md](../../docs/BACKPACK_CURIOS_FIX_DESIGN.md).

## Problem

Curios 17's `getStackInSlot` returns a copy. Traveler's Backpack 11.4.0 writes worn-backpack changes (storage, tools,
upgrades, settings, starter upgrades, passive ticking, abilities) into whatever stack it is given, so those changes
were written to a copy and lost.

## What the mod changes

The fix applies only on the logical server, and only while TB's Curios integration is active
(`TravelersBackpack.enableIntegration()` and `enableCurios()`).

| Mixin | Target | Change |
|---|---|---|
| `CuriosStacksResourceHandlerMixin` | Curios `CuriosStacksResourceHandler` | Adds a method, private to this addon, that returns the stored slot stack. Curios' public getters still return copies. |
| `AttachmentUtilsMixin` | TB `AttachmentUtils.getWearingBackpack` (entry E1) | Returns the stored stack instead of TB's copy, after checking that the two match. |
| `TravelersBackpackCurioMixin` | TB `TravelersBackpackCurio.curioTick` → `BackpackWrapper.tick` (entry E2) | Passes the stored stack of the ticked slot to `tick`. |
| `BackpackItemMenuMixin`, `BackpackSettingsMenuMixin` | `stillValid` | Keeps TB's owner and liveness checks. A worn menu is also only valid while its wrapper still wraps the stored stack. |
| `BackpackWrapperMixin` | `BackpackWrapper.getBackpackWrapper(Player, ItemStack, int[])` | If the open-menu wrapper TB would reuse is stale, closes its menus and returns a wrapper built on the stored stack. |

A stale wrapper is detected by object identity. Curios replaces the stored object on every set, insert, extract,
rollback, deserialize, and resize. A moved, removed, or replaced bag is therefore detected even when the replacement
has identical contents, and an old wrapper cannot write into the replacement.

Held backpacks, placed backpacks, and native-attachment backpacks keep TB's original behaviour. The mod adds no
registries, network payloads, or data formats, so clients do not need it for multiplayer. Client pack 1.1.12 and
later bundle the same jar so singleplayer worlds (integrated server) get the same fix; that use was not run-tested.
The four version pins in `neoforge.mods.toml` are declared `side="SERVER"`, so on a client the pack's own pinned
versions keep the combination exact.

## Constraints

- Mutating the stored stack bypasses the transfer handler's `set`, `onContentsChanged`, and snapshot journal. This is
  only acceptable for the pinned versions. `CuriosStacksResourceHandler` has no content callback, and the TB paths
  involved never run inside a transfer transaction. Curios still saves and syncs the changes through its normal
  serialization and its per-tick change detection.
- An unexpected state throws `IllegalStateException` instead of falling back to copies. The unexpected states are: a
  Curios handler class other than the expected one, a copy that differs from the stored stack, a non-backpack item in
  the resolved slot, more than one worn backpack, and a stale wrapper that no open menu holds.
- Any version change needs a fresh review and a fresh runtime test. `neoforge.mods.toml` pins all four versions
  exactly, and the mixins are `required` with `defaultRequire = 1`.

## Build

```sh
python3 compat/backpack-curios/build.py
```

The build needs Docker and the `eclipse-temurin:25-jdk` image pinned by digest
`eclipse-temurin@sha256:97014c4b396021f9ddb7d592a7dbedb0c4e4215c29e03dc01c393558aefb71c2`. Docker only pulls it if it is
missing, and the pull fails rather than using a different JDK. It compiles with `javac --release 25 -proc:none` in a
container without network access. It compiles against `server-data-26.3-neoforge/libraries`, the installed TB and
Curios jars, and MixinExtras 0.5.4 extracted from the NeoForge jar. The unpatched vanilla server jar and installertools
are excluded.

Before compiling, the build checks the pinned SHA-256 hashes of these inputs: TB, Curios, NeoForge, the patched
Minecraft jar, sponge-mixin, MixinExtras, and a digest over the whole library set. After an intentional, reviewed
dependency change, print the new library digest with `build.py --print-library-digest`.

The jar is deterministic: sorted entries and fixed timestamps. The build writes
`dist/backpack-curios/aziran-backpack-curios-1.0.0.jar` and a `.sha256` file next to it.

## Test

Tests are owned by Codex, under `tests/backpack-runtime/`:

```sh
python3 tests/backpack-runtime/run.py --patch dist/backpack-curios/aziran-backpack-curios-1.0.0.jar
```
