        def to_int_tuple(key):
            # workaround for uint64 indexer (GH:1406)
            # TODO remove here after next dask release (0.15.3)
            return tuple([k.astype(int) if isinstance(k, np.ndarray)
                          else int(k) if isinstance(k, np.integer) else k
                          for k in key])