    def tile(cls, op: "DataFrameGroupByAgg"):
        if op.method == 'auto':
            ctx = get_context()
            if ctx is not None and ctx.running_mode == RunningMode.distributed:  # pragma: no cover
                return cls._tile_with_shuffle(op)
            else:
                return cls._tile_with_tree(op)
        if op.method == 'shuffle':
            return cls._tile_with_shuffle(op)
        elif op.method == 'tree':
            return cls._tile_with_tree(op)
        else:  # pragma: no cover
            raise NotImplementedError