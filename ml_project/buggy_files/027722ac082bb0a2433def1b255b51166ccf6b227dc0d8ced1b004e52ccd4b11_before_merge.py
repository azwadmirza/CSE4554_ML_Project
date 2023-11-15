    def groupby_reduce(cls, axis, partitions, by, map_func, reduce_func):
        by_parts = np.squeeze(by)
        if len(by_parts.shape) == 0:
            by_parts = np.array([by_parts.item()])
        [obj.drain_call_queue() for obj in by_parts]
        new_partitions = np.array(
            [
                [
                    part.add_to_apply_calls(
                        map_func,
                        other=by_parts[col_idx].get()
                        if axis
                        else by_parts[row_idx].get(),
                    )
                    for col_idx, part in enumerate(partitions[row_idx])
                ]
                for row_idx in range(len(partitions))
            ]
        )
        return cls.map_axis_partitions(axis, new_partitions, reduce_func)