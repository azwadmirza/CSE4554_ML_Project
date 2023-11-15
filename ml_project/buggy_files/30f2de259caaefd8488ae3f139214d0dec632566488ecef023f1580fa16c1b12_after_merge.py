    def process(self,
                index_info: IndexInfo,
                context: IndexHandlerContext) -> None:
        tileable = context.tileable
        input_axis = index_info.input_axis
        is_first_bool_index = self._is_first_bool_index(context, index_info)

        axes = list(range(input_axis, input_axis + index_info.raw_index.ndim))
        cum_sizes = []
        for axis in axes:
            cum_sizes.append(np.cumsum((0,) + tileable.nsplits[axis]))

        other_index_to_iter = dict()
        for chunk_index, chunk_index_info in context.chunk_index_to_info.items():
            slcs = []
            for j, axis in enumerate(axes):
                axis_index = chunk_index[axis]
                slcs.append(slice(cum_sizes[j][axis_index],
                                  cum_sizes[j][axis_index + 1]))
            other_index = chunk_index[:axes[0]] + chunk_index[axes[-1] + 1:]
            if other_index not in other_index_to_iter:
                other_index_to_iter[other_index] = itertools.count()
            index = index_info.raw_index[tuple(slcs)]
            output_axis_index = next(other_index_to_iter[other_index])

            # if more than 1 bool index, getitem will rewrite them into fancy
            # but for now, setitem will keep them, thus we cannot record
            # index or shape for this one
            output_axis_index = None if not is_first_bool_index else output_axis_index
            output_size = None if not is_first_bool_index else int(index.sum())

            self.set_chunk_index_info(context, index_info, chunk_index,
                                      chunk_index_info, output_axis_index,
                                      index, output_size)