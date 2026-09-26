package uk.aziran.backpackcurios.mixin;

import java.util.Objects;
import net.minecraft.world.item.ItemStack;
import net.neoforged.neoforge.transfer.item.ItemStacksResourceHandler;
import org.spongepowered.asm.mixin.Mixin;
import top.theillusivec4.curios.common.inventory.CuriosStacksResourceHandler;
import uk.aziran.backpackcurios.StoredCurioStacks;

/**
 * Exposes the stored stack of a Curios slot to this addon only. Curios' public getStackInSlot keeps returning copies.
 *
 * <p>Callers that mutate the returned object bypass the transfer handler's set/onContentsChanged and snapshot
 * journal. That is acceptable only for the pinned versions: CuriosStacksResourceHandler has no content callback and
 * the Traveler's Backpack paths that use this never run inside a transfer transaction.
 */
@Mixin(value = CuriosStacksResourceHandler.class, remap = false)
public abstract class CuriosStacksResourceHandlerMixin extends ItemStacksResourceHandler implements StoredCurioStacks {
    private CuriosStacksResourceHandlerMixin() {
        super(0);
    }

    @Override
    public ItemStack aziran$storedStack(int index) {
        Objects.checkIndex(index, this.stacks.size());
        return this.stacks.get(index);
    }
}
