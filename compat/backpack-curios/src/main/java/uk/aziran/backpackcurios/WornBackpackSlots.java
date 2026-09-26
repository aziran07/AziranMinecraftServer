package uk.aziran.backpackcurios;

import com.tiviacz.travelersbackpack.TravelersBackpack;
import com.tiviacz.travelersbackpack.attachment.AttachmentUtils;
import com.tiviacz.travelersbackpack.inventory.BackpackWrapper;
import com.tiviacz.travelersbackpack.inventory.menu.AbstractBackpackMenu;
import com.tiviacz.travelersbackpack.item.TravelersBackpackItem;
import java.util.ArrayList;
import java.util.List;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import top.theillusivec4.curios.api.CuriosApi;
import top.theillusivec4.curios.api.SlotContext;
import top.theillusivec4.curios.api.SlotResult;
import top.theillusivec4.curios.api.type.capability.ICuriosItemHandler;
import top.theillusivec4.curios.api.type.inventory.IDynamicStackHandler;

/**
 * Resolves the backpack ItemStack that Curios actually stores for a player.
 *
 * <p>Curios 17 hands out copies from its public getters. Traveler's Backpack 11.4.0 writes worn-backpack changes into
 * whatever stack it is given, so it needs the stored object. That object is only handed to Traveler's Backpack's own
 * worn-backpack entry points on the logical server; everyone else still gets Curios' copies.
 *
 * <p>The stored object doubles as a freshness token. Curios replaces it on every set, insert, extract, transaction
 * rollback, deserialize and resize, so a wrapper holding an older object belongs to a bag that has since been moved,
 * removed or replaced, even when the replacement has identical contents.
 */
public final class WornBackpackSlots {
    private WornBackpackSlots() {
    }

    /** True when Traveler's Backpack uses the Curios Back slot and this is the logical server. */
    public static boolean isActive(LivingEntity entity) {
        return entity != null
            && !entity.level().isClientSide()
            && TravelersBackpack.enableIntegration()
            && TravelersBackpack.enableCurios();
    }

    /** The stored stack of the first worn backpack, as found by Traveler's Backpack's own Curios lookup. */
    public static ItemStack storedWornBackpack(Player player) {
        ICuriosItemHandler curios = curiosInventory(player);
        SlotResult result = curios.findFirstCurio(stack -> stack.getItem() instanceof TravelersBackpackItem)
            .orElseThrow(() -> new IllegalStateException(
                "Curios reports a worn Traveler's Backpack for " + player.getScoreboardName() + " but findFirstCurio found none"));
        return storedBackpack(player, curios, result.slotContext());
    }

    /** The stored stack in the functional Curios slot described by the context. */
    public static ItemStack storedBackpack(Player player, SlotContext slot) {
        return storedBackpack(player, curiosInventory(player), slot);
    }

    private static ItemStack storedBackpack(Player player, ICuriosItemHandler curios, SlotContext slot) {
        if (slot.cosmetic()) {
            throw new IllegalStateException("Worn backpack lookup resolved to a cosmetic Curios slot: " + describe(player, slot));
        }
        IDynamicStackHandler stacks = curios.getStacksHandler(slot.identifier())
            .orElseThrow(() -> new IllegalStateException("Curios slot type is missing: " + describe(player, slot)))
            .getStacks();
        if (!(stacks instanceof StoredCurioStacks storedStacks)) {
            throw new IllegalStateException("Unsupported Curios stack handler " + stacks.getClass().getName()
                + " (expected CuriosStacksResourceHandler): " + describe(player, slot));
        }
        ItemStack stored = storedStacks.aziran$storedStack(slot.index());
        if (!(stored.getItem() instanceof TravelersBackpackItem)) {
            throw new IllegalStateException("Curios slot does not hold a Traveler's Backpack: " + describe(player, slot) + " holds " + stored);
        }
        return stored;
    }

    /** Fails when Traveler's Backpack's detached copy does not describe the stored stack it was copied from. */
    public static void requireSameContents(ItemStack copy, ItemStack stored, Player player, String context) {
        if (!ItemStack.matches(copy, stored)) {
            throw new IllegalStateException("Curios copy and stored worn backpack differ for " + player.getScoreboardName()
                + " (" + context + "): copy=" + copy + ", stored=" + stored);
        }
    }

    /** True when the worn-backpack wrapper still wraps the bag that is stored in the owner's Curios slot right now. */
    public static boolean isCurrent(BackpackWrapper wrapper, Player owner) {
        return AttachmentUtils.isWearingBackpack(owner) && wrapper.getBackpackStack() == storedWornBackpack(owner);
    }

    /**
     * Closes every open Traveler's Backpack menu that uses the wrapper and returns how many were closed. Checks the
     * owner first because a player that is not in the level's player list (for example a FakePlayer) can still own a menu.
     */
    public static int closeMenusUsing(BackpackWrapper wrapper, Player owner) {
        List<Player> candidates = new ArrayList<>();
        candidates.add(owner);
        for (Player player : owner.level().players()) {
            if (player != owner) {
                candidates.add(player);
            }
        }
        int closed = 0;
        for (Player player : candidates) {
            if (player.containerMenu instanceof AbstractBackpackMenu menu && menu.getWrapper() == wrapper) {
                if (!(player instanceof ServerPlayer serverPlayer)) {
                    throw new IllegalStateException("Stale worn backpack menu is held by a non-server player: " + player);
                }
                serverPlayer.closeContainer();
                if (serverPlayer.containerMenu == menu) {
                    throw new IllegalStateException("Closing a stale worn backpack menu failed for " + player.getScoreboardName());
                }
                closed++;
            }
        }
        return closed;
    }

    private static ICuriosItemHandler curiosInventory(Player player) {
        return CuriosApi.getCuriosInventory(player)
            .orElseThrow(() -> new IllegalStateException("Player has no Curios inventory: " + player.getScoreboardName()));
    }

    private static String describe(Player player, SlotContext slot) {
        return player.getScoreboardName() + " " + slot.identifier() + "#" + slot.index();
    }
}
