    def preprocess(cls, op, in_data=None):
        if in_data is None:
            in_data = op.inputs[0]
        axis_shape = in_data.shape[op.axis]
        axis_chunk_shape = in_data.chunk_shape[op.axis]

        # rechunk to ensure all chunks on axis have rough same size
        has_unknown_shape = False
        for ns in in_data.nsplits:
            if any(np.isnan(s) for s in ns):
                has_unknown_shape = True
                break

        if not has_unknown_shape:
            axis_chunk_shape = min(axis_chunk_shape, int(np.sqrt(axis_shape)))
            if np.isnan(axis_shape) or any(np.isnan(s) for s in in_data.nsplits[op.axis]):
                raise TilesError('fail to tile because either the shape of '
                                 'input data on axis {} has unknown shape or chunk shape'.format(op.axis))
            chunk_size = int(axis_shape / axis_chunk_shape)
            chunk_sizes = [chunk_size for _ in range(int(axis_shape // chunk_size))]
            if axis_shape % chunk_size > 0:
                chunk_sizes[-1] += axis_shape % chunk_size
            in_data = in_data.rechunk({op.axis: tuple(chunk_sizes)})._inplace_tile()
            axis_chunk_shape = in_data.chunk_shape[op.axis]

        left_chunk_shape = in_data.chunk_shape[:op.axis] + in_data.chunk_shape[op.axis + 1:]
        if len(left_chunk_shape) > 0:
            out_idxes = itertools.product(*(range(s) for s in left_chunk_shape))
        else:
            out_idxes = [()]
        # if the size except axis has more than 1, the sorted values on each one may be different
        # another shuffle would be required to make sure each axis except to sort
        # has elements with identical size
        extra_shape = [s for i, s in enumerate(in_data.shape) if i != op.axis]
        if getattr(op, 'need_align', None) is None:
            need_align = bool(np.prod(extra_shape, dtype=int) != 1)
        else:
            need_align = op.need_align

        return in_data, axis_chunk_shape, out_idxes, need_align