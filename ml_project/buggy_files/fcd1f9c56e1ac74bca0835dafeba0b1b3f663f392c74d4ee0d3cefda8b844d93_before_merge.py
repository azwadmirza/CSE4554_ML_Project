    def _get_slice_axis(self, slice_obj, axis=0):
        obj = self.obj

        axis_name = obj._get_axis_name(axis)
        labels = getattr(obj, axis_name)

        int_slice = _is_index_slice(slice_obj)

        start = slice_obj.start
        stop = slice_obj.stop

        # in case of providing all floats, use label-based indexing
        float_slice = (labels.inferred_type == 'floating'
                       and (type(start) == float or start is None)
                       and (type(stop) == float or stop is None))

        null_slice = slice_obj.start is None and slice_obj.stop is None

        # could have integers in the first level of the MultiIndex, in which
        # case we wouldn't want to do position-based slicing
        position_slice = (int_slice
                          and labels.inferred_type != 'integer'
                          and not isinstance(labels, MultiIndex)
                          and not float_slice)

        # last ditch effort: if we are mixed and have integers
        try:
            if 'mixed' in labels.inferred_type and int_slice:
                if start is not None:
                    i = labels.get_loc(start)
                if stop is not None:
                    j = labels.get_loc(stop)
                position_slice = False
        except KeyError:
            if labels.inferred_type == 'mixed-integer':
                raise

        if null_slice or position_slice:
            slicer = slice_obj
        else:
            try:
                i, j = labels.slice_locs(start, stop)
                slicer = slice(i, j, slice_obj.step)
            except Exception:
                if _is_index_slice(slice_obj):
                    if labels.inferred_type == 'integer':
                        raise
                    slicer = slice_obj
                else:
                    raise

        if not _need_slice(slice_obj):
            return obj

        return self._slice(slicer, axis=axis)