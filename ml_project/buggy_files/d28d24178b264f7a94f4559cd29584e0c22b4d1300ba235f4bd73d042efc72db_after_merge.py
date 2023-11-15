    def set(self, item, value, check=False):
        """
        Set new item in-place. Does not consolidate. Adds new Block if not
        contained in the current set of items
        if check, then validate that we are not setting the same data in-place
        """
        # FIXME: refactor, clearly separate broadcasting & zip-like assignment
        #        can prob also fix the various if tests for sparse/categorical

        value_is_extension_type = is_extension_type(value)

        # categorical/spares/datetimetz
        if value_is_extension_type:

            def value_getitem(placement):
                return value
        else:
            if value.ndim == self.ndim - 1:
                value = value.reshape((1,) + value.shape)

                def value_getitem(placement):
                    return value
            else:

                def value_getitem(placement):
                    return value[placement.indexer]

            if value.shape[1:] != self.shape[1:]:
                raise AssertionError('Shape of new values must be compatible '
                                     'with manager shape')

        try:
            loc = self.items.get_loc(item)
        except KeyError:
            # This item wasn't present, just insert at end
            self.insert(len(self.items), item, value)
            return

        if isinstance(loc, int):
            loc = [loc]

        blknos = self._blknos[loc]
        blklocs = self._blklocs[loc].copy()

        unfit_mgr_locs = []
        unfit_val_locs = []
        removed_blknos = []
        for blkno, val_locs in _get_blkno_placements(blknos, len(self.blocks),
                                                     group=True):
            blk = self.blocks[blkno]
            blk_locs = blklocs[val_locs.indexer]
            if blk.should_store(value):
                blk.set(blk_locs, value_getitem(val_locs), check=check)
            else:
                unfit_mgr_locs.append(blk.mgr_locs.as_array[blk_locs])
                unfit_val_locs.append(val_locs)

                # If all block items are unfit, schedule the block for removal.
                if len(val_locs) == len(blk.mgr_locs):
                    removed_blknos.append(blkno)
                else:
                    self._blklocs[blk.mgr_locs.indexer] = -1
                    blk.delete(blk_locs)
                    self._blklocs[blk.mgr_locs.indexer] = np.arange(len(blk))

        if len(removed_blknos):
            # Remove blocks & update blknos accordingly
            is_deleted = np.zeros(self.nblocks, dtype=np.bool_)
            is_deleted[removed_blknos] = True

            new_blknos = np.empty(self.nblocks, dtype=np.int64)
            new_blknos.fill(-1)
            new_blknos[~is_deleted] = np.arange(self.nblocks -
                                                len(removed_blknos))
            self._blknos = algos.take_1d(new_blknos, self._blknos, axis=0,
                                         allow_fill=False)
            self.blocks = tuple(blk for i, blk in enumerate(self.blocks)
                                if i not in set(removed_blknos))

        if unfit_val_locs:
            unfit_mgr_locs = np.concatenate(unfit_mgr_locs)
            unfit_count = len(unfit_mgr_locs)

            new_blocks = []
            if value_is_extension_type:
                # This code (ab-)uses the fact that sparse blocks contain only
                # one item.
                new_blocks.extend(
                    make_block(values=value.copy(), ndim=self.ndim,
                               placement=slice(mgr_loc, mgr_loc + 1))
                    for mgr_loc in unfit_mgr_locs)

                self._blknos[unfit_mgr_locs] = (np.arange(unfit_count) +
                                                len(self.blocks))
                self._blklocs[unfit_mgr_locs] = 0

            else:
                # unfit_val_locs contains BlockPlacement objects
                unfit_val_items = unfit_val_locs[0].append(unfit_val_locs[1:])

                new_blocks.append(
                    make_block(values=value_getitem(unfit_val_items),
                               ndim=self.ndim, placement=unfit_mgr_locs))

                self._blknos[unfit_mgr_locs] = len(self.blocks)
                self._blklocs[unfit_mgr_locs] = np.arange(unfit_count)

            self.blocks += tuple(new_blocks)

            # Newly created block's dtype may already be present.
            self._known_consolidated = False