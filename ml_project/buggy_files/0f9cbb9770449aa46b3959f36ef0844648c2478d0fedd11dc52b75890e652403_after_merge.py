    def _get_chunk_index_min_max(cls, df, index_type, axis):
        index = getattr(df, index_type)

        chunk_index_min_max = []
        for i in range(df.chunk_shape[axis]):
            chunk_idx = [0, 0]
            chunk_idx[axis] = i
            chunk = df.cix[tuple(chunk_idx)]
            chunk_index = getattr(chunk, index_type)
            min_val = chunk_index.min_val
            min_val_close = chunk_index.min_val_close
            max_val = chunk_index.max_val
            max_val_close = chunk_index.max_val_close
            if min_val is None or max_val is None:
                return
            chunk_index_min_max.append((min_val, min_val_close, max_val, max_val_close))

        if index.is_monotonic_decreasing:
            return list(reversed(chunk_index_min_max)), False

        if cls._check_overlap(chunk_index_min_max):
            return
        return chunk_index_min_max, True