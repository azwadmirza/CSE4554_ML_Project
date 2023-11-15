    def _setitem_with_indexer(self, indexer, value):
        self._has_valid_setitem_indexer(indexer)

        # also has the side effect of consolidating in-place
        from pandas import Panel, DataFrame, Series
        info_axis = self.obj._info_axis_number

        # maybe partial set
        take_split_path = self.obj._is_mixed_type

        # if there is only one block/type, still have to take split path
        # unless the block is one-dimensional or it can hold the value
        if not take_split_path and self.obj._data.blocks:
            blk, = self.obj._data.blocks
            if 1 < blk.ndim:  # in case of dict, keys are indices
                val = list(value.values()) if isinstance(value,dict) else value
                take_split_path = not blk._can_hold_element(val)

        if isinstance(indexer, tuple) and len(indexer) == len(self.obj.axes):

            for i, ax in zip(indexer, self.obj.axes):

                # if we have any multi-indexes that have non-trivial slices (not null slices)
                # then we must take the split path, xref GH 10360
                if isinstance(ax, MultiIndex) and not (is_integer(i) or is_null_slice(i)):
                    take_split_path = True
                    break

        if isinstance(indexer, tuple):
            nindexer = []
            for i, idx in enumerate(indexer):
                if isinstance(idx, dict):

                    # reindex the axis to the new value
                    # and set inplace
                    key, _ = convert_missing_indexer(idx)

                    # if this is the items axes, then take the main missing
                    # path first
                    # this correctly sets the dtype and avoids cache issues
                    # essentially this separates out the block that is needed
                    # to possibly be modified
                    if self.ndim > 1 and i == self.obj._info_axis_number:

                        # add the new item, and set the value
                        # must have all defined axes if we have a scalar
                        # or a list-like on the non-info axes if we have a
                        # list-like
                        len_non_info_axes = [
                            len(_ax) for _i, _ax in enumerate(self.obj.axes)
                            if _i != i
                        ]
                        if any([not l for l in len_non_info_axes]):
                            if not is_list_like_indexer(value):
                                raise ValueError("cannot set a frame with no "
                                                 "defined index and a scalar")
                            self.obj[key] = value
                            return self.obj


                        # add a new item with the dtype setup
                        self.obj[key] = _infer_fill_value(value)

                        new_indexer = convert_from_missing_indexer_tuple(
                            indexer, self.obj.axes)
                        self._setitem_with_indexer(new_indexer, value)

                        return self.obj

                    # reindex the axis
                    # make sure to clear the cache because we are
                    # just replacing the block manager here
                    # so the object is the same
                    index = self.obj._get_axis(i)
                    labels = index.insert(len(index),key)
                    self.obj._data = self.obj.reindex_axis(labels, i)._data
                    self.obj._maybe_update_cacher(clear=True)
                    self.obj.is_copy=None

                    nindexer.append(labels.get_loc(key))

                else:
                    nindexer.append(idx)

            indexer = tuple(nindexer)
        else:

            indexer, missing = convert_missing_indexer(indexer)

            if missing:

                # reindex the axis to the new value
                # and set inplace
                if self.ndim == 1:
                    index = self.obj.index
                    new_index = index.insert(len(index),indexer)

                    # this preserves dtype of the value
                    new_values = Series([value]).values
                    if len(self.obj.values):
                        new_values = np.concatenate([self.obj.values,
                                                     new_values])

                    self.obj._data = self.obj._constructor(
                        new_values, index=new_index, name=self.obj.name)._data
                    self.obj._maybe_update_cacher(clear=True)
                    return self.obj

                elif self.ndim == 2:

                    # no columns and scalar
                    if not len(self.obj.columns):
                        raise ValueError(
                            "cannot set a frame with no defined columns"
                        )

                    # append a Series
                    if isinstance(value, Series):

                        value = value.reindex(index=self.obj.columns,copy=True)
                        value.name = indexer

                    # a list-list
                    else:

                        # must have conforming columns
                        if is_list_like_indexer(value):
                            if len(value) != len(self.obj.columns):
                                raise ValueError(
                                    "cannot set a row with mismatched columns"
                                    )

                        value = Series(value,index=self.obj.columns,name=indexer)

                    self.obj._data = self.obj.append(value)._data
                    self.obj._maybe_update_cacher(clear=True)
                    return self.obj

                # set using setitem (Panel and > dims)
                elif self.ndim >= 3:
                    return self.obj.__setitem__(indexer, value)

        # set
        item_labels = self.obj._get_axis(info_axis)

        # align and set the values
        if take_split_path:

            if not isinstance(indexer, tuple):
                indexer = self._tuplify(indexer)

            if isinstance(value, ABCSeries):
                value = self._align_series(indexer, value)

            info_idx = indexer[info_axis]
            if is_integer(info_idx):
                info_idx = [info_idx]
            labels = item_labels[info_idx]

            # if we have a partial multiindex, then need to adjust the plane
            # indexer here
            if (len(labels) == 1 and
                    isinstance(self.obj[labels[0]].axes[0], MultiIndex)):
                item = labels[0]
                obj = self.obj[item]
                index = obj.index
                idx = indexer[:info_axis][0]

                plane_indexer = tuple([idx]) + indexer[info_axis + 1:]
                lplane_indexer = length_of_indexer(plane_indexer[0], index)

                # require that we are setting the right number of values that
                # we are indexing
                if is_list_like_indexer(value) and np.iterable(value) and lplane_indexer != len(value):

                    if len(obj[idx]) != len(value):
                        raise ValueError(
                            "cannot set using a multi-index selection indexer "
                            "with a different length than the value"
                        )

                    # make sure we have an ndarray
                    value = getattr(value,'values',value).ravel()

                    # we can directly set the series here
                    # as we select a slice indexer on the mi
                    idx = index._convert_slice_indexer(idx)
                    obj._consolidate_inplace()
                    obj = obj.copy()
                    obj._data = obj._data.setitem(indexer=tuple([idx]), value=value)
                    self.obj[item] = obj
                    return

            # non-mi
            else:
                plane_indexer = indexer[:info_axis] + indexer[info_axis + 1:]
                if info_axis > 0:
                    plane_axis = self.obj.axes[:info_axis][0]
                    lplane_indexer = length_of_indexer(plane_indexer[0],
                                                       plane_axis)
                else:
                    lplane_indexer = 0

            def setter(item, v):
                s = self.obj[item]
                pi = plane_indexer[0] if lplane_indexer == 1 else plane_indexer

                # perform the equivalent of a setitem on the info axis
                # as we have a null slice or a slice with full bounds
                # which means essentially reassign to the columns of a multi-dim object
                # GH6149 (null slice), GH10408 (full bounds)
                if isinstance(pi, tuple) and all(is_null_slice(idx) or is_full_slice(idx, len(self.obj)) for idx in pi):
                    s = v
                else:
                    # set the item, possibly having a dtype change
                    s._consolidate_inplace()
                    s = s.copy()
                    s._data = s._data.setitem(indexer=pi, value=v)
                    s._maybe_update_cacher(clear=True)

                # reset the sliced object if unique
                self.obj[item] = s

            def can_do_equal_len():
                """ return True if we have an equal len settable """
                if not len(labels) == 1 or not np.iterable(value):
                    return False

                l = len(value)
                item = labels[0]
                index = self.obj[item].index

                # equal len list/ndarray
                if len(index) == l:
                    return True
                elif lplane_indexer == l:
                    return True

                return False

            # we need an iterable, with a ndim of at least 1
            # eg. don't pass through np.array(0)
            if is_list_like_indexer(value) and getattr(value,'ndim',1) > 0:

                # we have an equal len Frame
                if isinstance(value, ABCDataFrame) and value.ndim > 1:

                    for item in labels:
                        # align to
                        v = np.nan if item not in value else \
                                self._align_series(indexer[0], value[item])
                        setter(item, v)

                # we have an equal len ndarray/convertible to our labels
                elif np.array(value).ndim == 2:

                    # note that this coerces the dtype if we are mixed
                    # GH 7551
                    value = np.array(value,dtype=object)
                    if len(labels) != value.shape[1]:
                        raise ValueError('Must have equal len keys and value '
                                         'when setting with an ndarray')

                    for i, item in enumerate(labels):

                        # setting with a list, recoerces
                        setter(item, value[:, i].tolist())

                # we have an equal len list/ndarray
                elif can_do_equal_len():
                    setter(labels[0], value)

                # per label values
                else:

                    if len(labels) != len(value):
                        raise ValueError('Must have equal len keys and value '
                                         'when setting with an iterable')

                    for item, v in zip(labels, value):
                        setter(item, v)
            else:

                # scalar
                for item in labels:
                    setter(item, value)

        else:
            if isinstance(indexer, tuple):
                indexer = maybe_convert_ix(*indexer)

                # if we are setting on the info axis ONLY
                # set using those methods to avoid block-splitting
                # logic here
                if len(indexer) > info_axis and is_integer(indexer[info_axis]) and all(
                    is_null_slice(idx) for i, idx in enumerate(indexer) if i != info_axis):
                    self.obj[item_labels[indexer[info_axis]]] = value
                    return

            if isinstance(value, (ABCSeries, dict)):
                value = self._align_series(indexer, Series(value))

            elif isinstance(value, ABCDataFrame):
                value = self._align_frame(indexer, value)

            if isinstance(value, ABCPanel):
                value = self._align_panel(indexer, value)

            # check for chained assignment
            self.obj._check_is_chained_assignment_possible()

            # actually do the set
            self.obj._consolidate_inplace()
            self.obj._data = self.obj._data.setitem(indexer=indexer, value=value)
            self.obj._maybe_update_cacher(clear=True)