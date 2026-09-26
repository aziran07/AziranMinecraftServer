package uk.aziran.backpackcurios.mixin;

import com.tiviacz.travelersbackpack.attachment.AttachmentUtils;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;
import uk.aziran.backpackcurios.WornBackpackSlots;

/** Entry point E1: every worn-backpack wrapper, menu and action starts from getWearingBackpack. */
@Mixin(value = AttachmentUtils.class, remap = false)
public abstract class AttachmentUtilsMixin {
    @Inject(method = "getWearingBackpack", at = @At("RETURN"), cancellable = true)
    private static void aziran$returnStoredWornBackpack(Player player, CallbackInfoReturnable<ItemStack> cir) {
        ItemStack copy = cir.getReturnValue();
        if (copy.isEmpty() || !WornBackpackSlots.isActive(player)) {
            return;
        }
        ItemStack stored = WornBackpackSlots.storedWornBackpack(player);
        WornBackpackSlots.requireSameContents(copy, stored, player, "getWearingBackpack");
        cir.setReturnValue(stored);
    }
}
