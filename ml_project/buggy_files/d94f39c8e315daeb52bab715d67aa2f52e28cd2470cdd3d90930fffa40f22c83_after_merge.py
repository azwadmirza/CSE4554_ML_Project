    def shift(self, periods, axis=0):
        """ shift the block by periods, possibly upcast """
        # convert integer to float if necessary. need to do a lot more than
        # that, handle boolean etc also
        new_values, fill_value = com._maybe_upcast(self.values)
        # make sure array sent to np.roll is c_contiguous
        f_ordered = new_values.flags.f_contiguous
        if f_ordered:
            new_values = new_values.T
            axis = new_values.ndim - axis - 1

        if np.prod(new_values.shape):
            new_values = np.roll(new_values, periods, axis=axis)

        axis_indexer = [ slice(None) ] * self.ndim
        if periods > 0:
            axis_indexer[axis] = slice(None,periods)
        else:
            axis_indexer[axis] = slice(periods,None)
        new_values[tuple(axis_indexer)] = fill_value

        # restore original order
        if f_ordered:
            new_values = new_values.T

        return [make_block(new_values,
                           ndim=self.ndim, fastpath=True,
                           placement=self.mgr_locs)]