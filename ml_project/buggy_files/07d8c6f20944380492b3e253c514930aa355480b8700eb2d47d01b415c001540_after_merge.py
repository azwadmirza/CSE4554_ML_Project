    def get_chunk_metas(self, chunk_keys, filter_fields=None):
        metas = []
        for chunk_key in chunk_keys:
            chunk_data = self.get(chunk_key)
            if chunk_data is None:
                metas.append(None)
                continue
            if hasattr(chunk_data, 'nbytes'):
                # ndarray
                size = chunk_data.nbytes
                shape = chunk_data.shape
            elif hasattr(chunk_data, 'memory_usage'):
                # DataFrame
                size = chunk_data.memory_usage(deep=True).sum()
                shape = chunk_data.shape
            else:
                # other
                size = sys.getsizeof(chunk_data)
                shape = ()

            metas.append(ChunkMeta(chunk_size=size, chunk_shape=shape, workers=None))

        selected_metas = []
        for chunk_meta in metas:
            if filter_fields is not None:
                chunk_meta = [getattr(chunk_meta, field) for field in filter_fields]
            selected_metas.append(chunk_meta)
        return selected_metas