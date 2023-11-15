    def __getitem__(self, key):
        def to_int_tuple(key):
            # workaround for uint64 indexer (GH:1406)
            # TODO remove here after next dask release (0.15.3)
            return tuple([k.astype(int) if isinstance(k, np.ndarray)
                          else k for k in key])

        if isinstance(key, BasicIndexer):
            return self.array[to_int_tuple(key)]
        elif isinstance(key, VectorizedIndexer):
            return self.array.vindex[to_int_tuple(tuple(key))]
        elif key is Ellipsis:
            return self.array
        else:
            assert isinstance(key, OuterIndexer)
            key = to_int_tuple(tuple(key))
            try:
                return self.array[key]
            except NotImplementedError:
                # manual orthogonal indexing.
                # TODO: port this upstream into dask in a saner way.
                value = self.array
                for axis, subkey in reversed(list(enumerate(key))):
                    value = value[(slice(None),) * axis + (subkey,)]
                return value