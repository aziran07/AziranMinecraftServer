package uk.aziran.backpacktests;

import com.google.gson.Gson;
import com.mojang.authlib.GameProfile;
import com.tiviacz.travelersbackpack.attachment.AttachmentUtils;
import com.tiviacz.travelersbackpack.config.TravelersBackpackConfig;
import com.tiviacz.travelersbackpack.init.ModDataComponents;
import com.tiviacz.travelersbackpack.init.ModItems;
import com.tiviacz.travelersbackpack.inventory.BackpackWrapper;
import com.tiviacz.travelersbackpack.inventory.menu.BackpackItemMenu;
import com.tiviacz.travelersbackpack.inventory.menu.BackpackSettingsMenu;
import java.io.IOException;
import java.io.UncheckedIOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicInteger;
import net.minecraft.server.MinecraftServer;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.NbtAccounter;
import net.minecraft.nbt.NbtIo;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.component.ItemContainerContents;
import net.neoforged.fml.common.Mod;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.common.util.FakePlayer;
import net.neoforged.neoforge.event.server.ServerStartedEvent;
import net.neoforged.neoforge.event.tick.EntityTickEvent;
import net.neoforged.neoforge.transfer.item.ItemResource;
import net.neoforged.neoforge.transfer.item.ItemStacksResourceHandler;
import net.neoforged.neoforge.transfer.item.ItemUtil;
import top.theillusivec4.curios.api.CuriosApi;
import top.theillusivec4.curios.api.SlotContext;
import top.theillusivec4.curios.api.type.capability.ICuriosItemHandler;
import top.theillusivec4.curios.api.type.inventory.IDynamicStackHandler;

/** Test-only mod: runs against real jars in a disposable dedicated-server world. */
@Mod("aziran_backpack_tests")
public final class BackpackPersistenceTests {
    private final Map<String, String> results = new LinkedHashMap<>();

    public BackpackPersistenceTests() {
        NeoForge.EVENT_BUS.addListener(this::serverStarted);
    }

    private void serverStarted(ServerStartedEvent event) {
        MinecraftServer server = event.getServer();
        server.execute(() -> {
            if (System.getProperty("aziran.backpackTestPhase", "write").equals("read")) {
                run("curios_contents_survive_server_process_restart", () -> readDurable(server));
            } else {
            run("curios_getter_stays_detached", () -> getterContract(server));
            run("worn_menu_close_reopen", () -> closeReopen(server));
            run("curios_inventory_serialization", () -> serialization(server));
            run("tools_upgrades_settings", () -> components(server));
            run("starter_upgrade_consumed_once", () -> starterUpgrade(server));
            run("open_menu_wrapper_reuse", () -> menuReuse(server));
            run("held_wrapper_leaves_curios_unchanged", () -> heldWrapper(server));
            run("native_wrapper_leaves_curios_unchanged", () -> nativeWrapper(server));
            run("placed_wrapper_preserves_save_callback", () -> placedWrapper(server));
            run("curio_tick_component_persists", () -> curioTick(server));
            run("curios_tick_observes_stored_contents", () -> curiosTickSync(server));
            run("stale_replaced_bag", () -> staleMenu(server, "different"));
            run("stale_identical_bag", () -> staleMenu(server, "identical"));
            run("stale_removed_bag", () -> staleMenu(server, "removed"));
            run("stale_settings_menu", () -> staleSettings(server));
            run("write_curios_restart_fixture", () -> writeDurable(server));
            }
            try {
                Path report = Path.of(System.getProperty("aziran.backpackTestReport", "backpack-tests-result.json"));
                Files.writeString(report, new Gson().toJson(results));
            } catch (Exception failure) {
                throw new IllegalStateException("Cannot write backpack test report", failure);
            } finally {
                server.halt(false);
            }
        });
    }

    private void run(String name, Runnable test) {
        try {
            test.run();
            results.put(name, "PASS");
            System.out.println("BACKPACK_TEST PASS " + name);
        } catch (Exception | AssertionError failure) {
            results.put(name, "FAIL: " + failure);
            System.err.println("BACKPACK_TEST FAIL " + name);
            failure.printStackTrace();
        }
    }

    private static Fixture fixture(MinecraftServer server) {
        FakePlayer player = new FakePlayer(server.overworld(), new GameProfile(UUID.randomUUID(), "BackpackTest"));
        ICuriosItemHandler inventory = CuriosApi.getCuriosInventory(player).orElseThrow();
        inventory.reset();
        IDynamicStackHandler back = inventory.getStacksHandler("back").orElseThrow().getStacks();
        check(back.getSlots() > 0, "Back slot must be provided by the real mod datapacks");
        back.setStackInSlot(0, new ItemStack(ModItems.STANDARD_TRAVELERS_BACKPACK.get()));
        return new Fixture(player, inventory, back);
    }

    private static BackpackItemMenu open(Fixture fixture) {
        BackpackWrapper wrapper = AttachmentUtils.getBackpackWrapper(fixture.player());
        check(wrapper != null && wrapper.getScreenID() == 2, "Must open a worn backpack");
        BackpackItemMenu menu = new BackpackItemMenu(1, fixture.player().getInventory(), wrapper);
        fixture.player().containerMenu = menu;
        return menu;
    }

    private static void close(Fixture fixture, BackpackItemMenu menu) {
        menu.removed(fixture.player());
        fixture.player().containerMenu = fixture.player().inventoryMenu;
    }

    private static void set(ItemStacksResourceHandler handler, int slot, ItemStack stack) {
        handler.set(slot, ItemResource.of(stack), stack.getCount());
    }

    private static void expect(ItemStack actual, ItemStack expected, String message) {
        check(ItemStack.matches(actual, expected), message + ": expected " + expected + ", got " + actual);
    }

    private static void check(boolean condition, String message) {
        if (!condition) throw new AssertionError(message);
    }

    private static void getterContract(MinecraftServer server) {
        Fixture fixture = fixture(server);
        ItemStack original = fixture.back().getStackInSlot(0);
        ItemStack copy = fixture.back().getStackInSlot(0);
        copy.set(ModDataComponents.COOLDOWN.get(), 1234);
        expect(fixture.back().getStackInSlot(0), original, "Curios getter must still return a detached stack");
    }

    private static void closeReopen(MinecraftServer server) {
        Fixture fixture = fixture(server);
        BackpackItemMenu first = open(fixture);
        ItemStack nuggets = new ItemStack(Items.IRON_NUGGET, 2);
        set(first.getWrapper().getStorage(), 0, nuggets);
        close(fixture, first);
        BackpackItemMenu second = open(fixture);
        expect(ItemUtil.getStack(second.getWrapper().getStorage(), 0), nuggets, "Closing a worn menu must preserve contents");
        set(second.getWrapper().getStorage(), 0, new ItemStack(Items.IRON_NUGGET, 1));
        close(fixture, second);
        BackpackItemMenu third = open(fixture);
        expect(ItemUtil.getStack(third.getWrapper().getStorage(), 0), new ItemStack(Items.IRON_NUGGET, 1), "Removing one item must persist");
        set(third.getWrapper().getStorage(), 0, ItemStack.EMPTY);
        close(fixture, third);
        BackpackItemMenu fourth = open(fixture);
        check(ItemUtil.getStack(fourth.getWrapper().getStorage(), 0).isEmpty(), "Removed items must not reappear");
        close(fixture, fourth);
    }

    private static void serialization(MinecraftServer server) {
        Fixture source = fixture(server);
        BackpackItemMenu menu = open(source);
        ItemStack diamonds = new ItemStack(Items.DIAMOND, 3);
        set(menu.getWrapper().getStorage(), 4, diamonds);
        close(source, menu);
        var saved = source.inventory().saveInventory(false).copy();
        Fixture restored = fixture(server);
        restored.back().setStackInSlot(0, ItemStack.EMPTY);
        restored.inventory().loadInventory(saved);
        BackpackItemMenu reopened = open(restored);
        expect(ItemUtil.getStack(reopened.getWrapper().getStorage(), 4), diamonds, "Serialized Curios contents must survive a fresh player/wrapper");
        close(restored, reopened);
    }

    private static void components(MinecraftServer server) {
        Fixture fixture = fixture(server);
        BackpackItemMenu menu = open(fixture);
        ItemStack tool = new ItemStack(Items.IRON_PICKAXE);
        ItemStack upgrade = new ItemStack(ModItems.PICKUP_UPGRADE.get());
        set(menu.getWrapper().getTools(), 0, tool);
        set(menu.getWrapper().getUpgrades(), 0, upgrade);
        menu.getWrapper().setCooldown(321);
        close(fixture, menu);
        BackpackItemMenu reopened = open(fixture);
        expect(ItemUtil.getStack(reopened.getWrapper().getTools(), 0), tool, "Tool slot must persist");
        expect(ItemUtil.getStack(reopened.getWrapper().getUpgrades(), 0), upgrade, "Upgrade slot must persist");
        check(reopened.getWrapper().getCooldown() == 321, "Backpack component changes must persist");
        close(fixture, reopened);
    }

    private static void starterUpgrade(MinecraftServer server) {
        Fixture fixture = fixture(server);
        ItemStack bag = fixture.back().getStackInSlot(0);
        ItemStack upgrade = new ItemStack(ModItems.CRAFTING_UPGRADE.get());
        bag.set(ModDataComponents.STARTER_UPGRADES.get(), ItemContainerContents.fromItems(List.of(upgrade)));
        fixture.back().setStackInSlot(0, bag);
        BackpackItemMenu menu = open(fixture);
        close(fixture, menu);
        ItemStack stored = fixture.back().getStackInSlot(0);
        check(!stored.has(ModDataComponents.STARTER_UPGRADES.get()), "Constructor must persist starter-upgrade consumption");
        BackpackItemMenu reopened = open(fixture);
        expect(ItemUtil.getStack(reopened.getWrapper().getUpgrades(), 0), upgrade, "Starter upgrade must be retained");
        check(ItemUtil.getStack(reopened.getWrapper().getUpgrades(), 1).isEmpty(), "Reopening must not duplicate starter upgrades");
        close(fixture, reopened);
    }

    private static void menuReuse(MinecraftServer server) {
        Fixture fixture = fixture(server);
        BackpackItemMenu menu = open(fixture);
        ItemStack emeralds = new ItemStack(Items.EMERALD, 7);
        set(menu.getWrapper().getStorage(), 2, emeralds);
        BackpackWrapper reused = AttachmentUtils.getBackpackWrapper(fixture.player());
        check(reused == menu.getWrapper(), "Normal lookup must reuse the open worn menu");
        reused.setCooldown(27);
        close(fixture, menu);
        BackpackItemMenu reopened = open(fixture);
        expect(ItemUtil.getStack(reopened.getWrapper().getStorage(), 2), emeralds, "Setting update must not revert stored items");
        close(fixture, reopened);
    }

    private static void heldWrapper(MinecraftServer server) {
        Fixture fixture = fixture(server);
        ItemStack before = fixture.back().getStackInSlot(0);
        ItemStack held = new ItemStack(ModItems.STANDARD_TRAVELERS_BACKPACK.get());
        BackpackWrapper wrapper = new BackpackWrapper(held, 1, fixture.player(), fixture.player().level());
        set(wrapper.getStorage(), 0, new ItemStack(Items.GOLD_INGOT, 5));
        expect(fixture.back().getStackInSlot(0), before, "Held wrapper must not alter the worn Curios backpack");
        expect(ItemUtil.getStack(new BackpackWrapper(held, 1, fixture.player(), fixture.player().level()).getStorage(), 0), new ItemStack(Items.GOLD_INGOT, 5), "Held stack contents must persist");
    }

    private static void nativeWrapper(MinecraftServer server) {
        Fixture fixture = fixture(server);
        ItemStack before = fixture.back().getStackInSlot(0);
        var setting = TravelersBackpackConfig.SERVER.backpackSettings.backSlotIntegration;
        boolean original = setting.get();
        setting.set(false);
        try {
            var attachment = AttachmentUtils.getAttachment(fixture.player()).orElseThrow();
            attachment.equipBackpack(new ItemStack(ModItems.STANDARD_TRAVELERS_BACKPACK.get()));
            BackpackItemMenu menu = open(fixture);
            set(menu.getWrapper().getStorage(), 0, new ItemStack(Items.GOLD_INGOT, 5));
            close(fixture, menu);
            BackpackItemMenu reopened = open(fixture);
            expect(ItemUtil.getStack(reopened.getWrapper().getStorage(), 0), new ItemStack(Items.GOLD_INGOT, 5), "Native attachment contents must persist");
            expect(fixture.back().getStackInSlot(0), before, "Native wrapper must not write into Curios");
            close(fixture, reopened);
        } finally {
            setting.set(original);
        }
    }

    private static void placedWrapper(MinecraftServer server) {
        Fixture fixture = fixture(server);
        ItemStack before = fixture.back().getStackInSlot(0);
        ItemStack placed = new ItemStack(ModItems.STANDARD_TRAVELERS_BACKPACK.get());
        BackpackWrapper wrapper = new BackpackWrapper(placed, 3, null, server.overworld());
        AtomicInteger saves = new AtomicInteger();
        wrapper.saveHandler = saves::incrementAndGet;
        set(wrapper.getStorage(), 0, new ItemStack(Items.GOLD_INGOT, 5));
        check(saves.get() > 0, "Placed wrapper save callback must run");
        expect(fixture.back().getStackInSlot(0), before, "Placed wrapper must not write into Curios");
    }

    private static void curioTick(MinecraftServer server) {
        Fixture fixture = fixture(server);
        ItemStack stack = fixture.back().getStackInSlot(0);
        stack.set(ModDataComponents.ABILITY_ENABLED.get(), true);
        fixture.back().setStackInSlot(0, stack);
        CuriosApi.getCurio(fixture.back().getStackInSlot(0)).orElseThrow()
            .curioTick(new SlotContext("back", fixture.player(), 0, false, true));
        check(!fixture.back().getStackInSlot(0).getOrDefault(ModDataComponents.ABILITY_ENABLED.get(), false),
            "Curio tick must persist disabling an unsupported standard-backpack ability");
    }

    private static void staleMenu(MinecraftServer server, String scenario) {
        Fixture fixture = fixture(server);
        BackpackItemMenu menu = open(fixture);
        ItemStack replacement = switch (scenario) {
            case "different" -> new ItemStack(ModItems.DIAMOND_TRAVELERS_BACKPACK.get());
            case "identical" -> fixture.back().getStackInSlot(0);
            case "removed" -> ItemStack.EMPTY;
            default -> throw new IllegalArgumentException(scenario);
        };
        fixture.back().setStackInSlot(0, replacement);
        check(!menu.stillValid(fixture.player()), "Menu must become invalid when its slot object is " + scenario);
        set(menu.getWrapper().getStorage(), 0, new ItemStack(Items.DIAMOND, 12));
        expect(fixture.back().getStackInSlot(0), replacement, "Orphaned wrapper must not overwrite the " + scenario + " slot");
        BackpackWrapper next = AttachmentUtils.getBackpackWrapper(fixture.player());
        if (scenario.equals("removed")) {
            check(next == null, "Removing the backpack must leave no worn wrapper");
        } else {
            check(next != null && next != menu.getWrapper(), "Lookup must discard a stale menu wrapper");
            check(ItemUtil.getStack(next.getStorage(), 0).isEmpty(), "Old contents must not leak into replacement");
        }
    }

    private static void curiosTickSync(MinecraftServer server) {
        Fixture fixture = fixture(server);
        BackpackItemMenu menu = open(fixture);
        ItemStack gold = new ItemStack(Items.GOLD_INGOT, 9);
        set(menu.getWrapper().getStorage(), 3, gold);
        NeoForge.EVENT_BUS.post(new EntityTickEvent.Post(fixture.player()));
        NeoForge.EVENT_BUS.post(new EntityTickEvent.Post(fixture.player()));
        ItemStack synchronizedStack = fixture.back().getPreviousStackInSlot(0);
        BackpackWrapper snapshot = new BackpackWrapper(synchronizedStack.copy(), 1, fixture.player(), fixture.player().level());
        expect(ItemUtil.getStack(snapshot.getStorage(), 3), gold, "Curios tick must observe stored contents for its synchronization snapshot");
        check(menu.stillValid(fixture.player()), "Ordinary Curios tick must not invalidate the live worn menu");
        close(fixture, menu);
    }

    private static void staleSettings(MinecraftServer server) {
        Fixture fixture = fixture(server);
        BackpackWrapper wrapper = AttachmentUtils.getBackpackWrapper(fixture.player());
        BackpackSettingsMenu menu = new BackpackSettingsMenu(2, fixture.player().getInventory(), wrapper);
        fixture.player().containerMenu = menu;
        ItemStack replacement = fixture.back().getStackInSlot(0);
        fixture.back().setStackInSlot(0, replacement);
        check(!menu.stillValid(fixture.player()), "Settings menu must become invalid after an identical bag replaces its owner");
        wrapper.setCooldown(1234);
        expect(fixture.back().getStackInSlot(0), replacement, "Stale settings must not change the replacement");
    }

    private static void writeDurable(MinecraftServer server) {
        Fixture fixture = fixture(server);
        BackpackItemMenu menu = open(fixture);
        set(menu.getWrapper().getStorage(), 5, new ItemStack(Items.IRON_NUGGET, 2));
        close(fixture, menu);
        CompoundTag saved = new CompoundTag();
        saved.put("Curios", fixture.inventory().saveInventory(false));
        try {
            NbtIo.writeCompressed(saved, Path.of("backpack-restart-fixture.dat"));
        } catch (IOException failure) {
            throw new UncheckedIOException("Cannot write Curios restart fixture", failure);
        }
    }

    private static void readDurable(MinecraftServer server) {
        Fixture fixture = fixture(server);
        fixture.back().setStackInSlot(0, ItemStack.EMPTY);
        try {
            CompoundTag saved = NbtIo.readCompressed(Path.of("backpack-restart-fixture.dat"), NbtAccounter.unlimitedHeap());
            fixture.inventory().loadInventory(saved.getList("Curios").orElseThrow());
        } catch (IOException failure) {
            throw new UncheckedIOException("Cannot read Curios restart fixture", failure);
        }
        BackpackItemMenu reopened = open(fixture);
        expect(ItemUtil.getStack(reopened.getWrapper().getStorage(), 5), new ItemStack(Items.IRON_NUGGET, 2),
            "Saved Curios contents must survive a separate JVM/server process");
        close(fixture, reopened);
    }

    private record Fixture(FakePlayer player, ICuriosItemHandler inventory, IDynamicStackHandler back) {}
}
