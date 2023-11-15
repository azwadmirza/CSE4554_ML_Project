    def concat(cls, axis, left_parts, right_parts):
        """Concatenate the blocks with another set of blocks.

        Note: Assumes that the blocks are already the same shape on the
            dimension being concatenated. A ValueError will be thrown if this
            condition is not met.

        Args:
            axis: The axis to concatenate to.
            right_parts: the other blocks to be concatenated. This is a
                BaseFrameManager object.

        Returns
        -------
            A new BaseFrameManager object, the type of object that called this.
        """
        if type(right_parts) is list:
            # `np.array` with partitions of empty ModinFrame has a shape (0,)
            # but `np.concatenate` can concatenate arrays only if its shapes at
            # specified axis are equals, so filtering empty frames to avoid concat error
            right_parts = [o for o in right_parts if o.size != 0]
            return np.concatenate([left_parts] + right_parts, axis=axis)
        else:
            return np.append(left_parts, right_parts, axis=axis)