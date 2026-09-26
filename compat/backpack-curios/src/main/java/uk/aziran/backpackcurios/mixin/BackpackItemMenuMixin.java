package uk.aziran.backpackcurios.mixin;

import com.tiviacz.travelersbackpack.inventory.BackpackWrapper;
import com.tiviacz.travelersbackpack.inventory.menu.BackpackItemMenu;
import net.minecraft.world.entity.player.Player;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;
import uk.aziran.backpackcurios.WornBackpackSlots;

/**
 * Adds an identity check to Traveler's Backpack's own owner/liveness validation for worn-backpack menus. Vanilla
 * checks stillValid before every click and closes invalid menus each player tick, so a menu whose bag was moved,
 * removed or replaced (even by an identical bag) stops accepting changes.
 */
@Mixin(value = BackpackItemMenu.class, remap = false)
public abstract class BackpackItemMenuMixin {
    @Inject(method = "stillValid", at = @At("RETURN"), cancellable = true)
    private void aziran$requireCurrentWornBackpack(Player player, CallbackInfoReturnable<Boolean> cir) {
        if (!cir.getReturnValueZ()) {
            return;
        }
        BackpackWrapper wrapper = ((BackpackItemMenu) (Object) this).getWrapper();
        Player owner = wrapper.getBackpackOwner();
        if (wrapper.getScreenID() != 2 || owner == null || !WornBackpackSlots.isActive(owner)) {
            return;
        }
        cir.setReturnValue(WornBackpackSlots.isCurrent(wrapper, owner));
    }
}
