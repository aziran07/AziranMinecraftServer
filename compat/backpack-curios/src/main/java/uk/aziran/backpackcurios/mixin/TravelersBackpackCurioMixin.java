package uk.aziran.backpackcurios.mixin;

import com.llamalad7.mixinextras.sugar.Local;
import com.tiviacz.travelersbackpack.compat.curios.TravelersBackpackCurio;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.ModifyArg;
import top.theillusivec4.curios.api.SlotContext;
import uk.aziran.backpackcurios.WornBackpackSlots;

/**
 * Entry point E2: Curios ticks a copy of the slot, and BackpackWrapper.tick mutates the stack it receives directly
 * (ability flag, cooldowns) and builds upgrade-ticking wrappers on it. Hand it the stored stack of the ticked slot.
 */
@Mixin(value = TravelersBackpackCurio.class, remap = false)
public abstract class TravelersBackpackCurioMixin {
    @ModifyArg(
        method = "curioTick",
        at = @At(
            value = "INVOKE",
            target = "Lcom/tiviacz/travelersbackpack/inventory/BackpackWrapper;tick(Lnet/minecraft/world/item/ItemStack;Lnet/minecraft/world/entity/player/Player;Z)V"
        ),
        index = 0
    )
    private ItemStack aziran$tickStoredBackpack(ItemStack tickCopy, @Local(argsOnly = true) SlotContext slotContext) {
        if (!(slotContext.entity() instanceof Player player) || !WornBackpackSlots.isActive(player)) {
            return tickCopy;
        }
        ItemStack stored = WornBackpackSlots.storedBackpack(player, slotContext);
        WornBackpackSlots.requireSameContents(tickCopy, stored, player, "curioTick");
        if (stored != WornBackpackSlots.storedWornBackpack(player)) {
            // Traveler's Backpack resolves every worn wrapper from the first worn bag only.
            throw new IllegalStateException("More than one worn Traveler's Backpack in Curios is unsupported: "
                + player.getScoreboardName() + " ticks " + slotContext.identifier() + "#" + slotContext.index());
        }
        return stored;
    }
}
