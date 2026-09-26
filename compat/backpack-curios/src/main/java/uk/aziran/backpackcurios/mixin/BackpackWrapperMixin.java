package uk.aziran.backpackcurios.mixin;

import com.tiviacz.travelersbackpack.inventory.BackpackWrapper;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;
import uk.aziran.backpackcurios.WornBackpackSlots;

/**
 * Worn-backpack wrapper lookup. Traveler's Backpack reuses the wrapper of any open worn menu for the owner before it
 * builds a new one on the given stack. A reused wrapper must still wrap the stored bag; otherwise its menus are closed
 * and the lookup runs again, which then builds a wrapper on the stored bag.
 */
@Mixin(value = BackpackWrapper.class, remap = false)
public abstract class BackpackWrapperMixin {
    @Inject(
        method = "getBackpackWrapper(Lnet/minecraft/world/entity/player/Player;Lnet/minecraft/world/item/ItemStack;[I)Lcom/tiviacz/travelersbackpack/inventory/BackpackWrapper;",
        at = @At("RETURN"),
        cancellable = true
    )
    private static void aziran$replaceStaleWornWrapper(Player player, ItemStack backpack, int[] dataLoad, CallbackInfoReturnable<BackpackWrapper> cir) {
        BackpackWrapper wrapper = cir.getReturnValue();
        if (wrapper == null || !WornBackpackSlots.isActive(player)) {
            return;
        }
        ItemStack stored = WornBackpackSlots.storedWornBackpack(player);
        if (backpack != stored) {
            // Worn wrappers built on anything but the stored stack would silently write into a copy.
            throw new IllegalStateException("Worn backpack wrapper requested for a stack that is not the stored Curios stack: player="
                + player.getScoreboardName() + ", given=" + backpack + ", stored=" + stored);
        }
        if (wrapper.getBackpackStack() == stored) {
            return;
        }
        if (WornBackpackSlots.closeMenusUsing(wrapper, player) == 0) {
            throw new IllegalStateException("Stale worn backpack wrapper for " + player.getScoreboardName() + " is not held by any open menu");
        }
        cir.setReturnValue(BackpackWrapper.getBackpackWrapper(player, backpack, dataLoad));
    }
}
