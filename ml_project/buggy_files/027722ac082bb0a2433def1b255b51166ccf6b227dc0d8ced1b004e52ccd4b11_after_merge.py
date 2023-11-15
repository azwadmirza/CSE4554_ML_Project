    def groupby_reduce(cls, axis, partitions, by, map_func, reduce_func):
        mapped_partitions = cls.broadcast_apply(
            axis, map_func, left=partitions, right=by, other_name="other"
        )
        return cls.map_axis_partitions(axis, mapped_partitions, reduce_func)