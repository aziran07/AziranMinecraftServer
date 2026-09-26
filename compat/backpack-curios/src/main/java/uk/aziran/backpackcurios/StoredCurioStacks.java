package uk.aziran.backpackcurios;

import net.minecraft.world.item.ItemStack;

/** Implemented on Curios' CuriosStacksResourceHandler by CuriosStacksResourceHandlerMixin. */
public interface StoredCurioStacks {
    /** Returns the ItemStack object the handler actually stores and serializes, not a copy. */
    ItemStack aziran$storedStack(int index);
}
