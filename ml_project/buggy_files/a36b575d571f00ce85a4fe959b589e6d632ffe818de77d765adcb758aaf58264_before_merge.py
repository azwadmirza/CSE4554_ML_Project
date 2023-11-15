    def _load_and_slice(self, dtype, var_path, shape, xslice, yslice):
        if isinstance(shape, tuple) and len(shape) == 2:
            return np.require(self[var_path][yslice, xslice], dtype=dtype)
        elif isinstance(shape, tuple) and len(shape) == 1:
            return np.require(self[var_path][yslice], dtype=dtype)
        else:
            return np.require(self[var_path][:], dtype=dtype)