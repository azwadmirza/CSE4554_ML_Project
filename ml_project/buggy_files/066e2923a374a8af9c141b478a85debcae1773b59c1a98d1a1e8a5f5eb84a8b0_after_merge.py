    def _setitem_single_block(self, indexer, value, name: str):
        """
        _setitem_with_indexer for the case when we have a single Block.
        """
        from pandas import Series

        info_axis = self.obj._info_axis_number
        item_labels = self.obj._get_axis(info_axis)

        if isinstance(indexer, tuple):

            # if we are setting on the info axis ONLY
            # set using those methods to avoid block-splitting
            # logic here
            if (
                len(indexer) > info_axis
                and is_integer(indexer[info_axis])
                and all(
                    com.is_null_slice(idx)
                    for i, idx in enumerate(indexer)
                    if i != info_axis
                )
            ):
                selected_item_labels = item_labels[indexer[info_axis]]
                if len(item_labels.get_indexer_for([selected_item_labels])) == 1:
                    self.obj[selected_item_labels] = value
                    return

            indexer = maybe_convert_ix(*indexer)
        if (isinstance(value, ABCSeries) and name != "iloc") or isinstance(value, dict):
            # TODO(EA): ExtensionBlock.setitem this causes issues with
            # setting for extensionarrays that store dicts. Need to decide
            # if it's worth supporting that.
            value = self._align_series(indexer, Series(value))

        elif isinstance(value, ABCDataFrame) and name != "iloc":
            value = self._align_frame(indexer, value)

        # check for chained assignment
        self.obj._check_is_chained_assignment_possible()

        # actually do the set
        self.obj._mgr = self.obj._mgr.setitem(indexer=indexer, value=value)
        self.obj._maybe_update_cacher(clear=True)