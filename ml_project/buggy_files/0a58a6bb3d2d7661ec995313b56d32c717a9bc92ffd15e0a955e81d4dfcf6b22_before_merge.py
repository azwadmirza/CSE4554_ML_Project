    def count(self):
        """ Compute count of group, excluding missing values """
        from functools import partial
        from pandas.core.dtypes.missing import _isna_ndarraylike as isna

        data, _ = self._get_data_to_aggregate()
        ids, _, ngroups = self.grouper.group_info
        mask = ids != -1

        val = ((mask & ~isna(blk.get_values())) for blk in data.blocks)
        loc = (blk.mgr_locs for blk in data.blocks)

        counter = partial(count_level_2d, labels=ids, max_bin=ngroups, axis=1)
        blk = map(make_block, map(counter, val), loc)

        return self._wrap_agged_blocks(data.items, list(blk))