    def _load_and_slice(self, var_path, shape, xslice, yslice):
        if isinstance(shape, tuple) and len(shape) == 2:
            return self[var_path][yslice, xslice]
        elif isinstance(shape, tuple) and len(shape) == 1:
            return self[var_path][yslice]
        else:
            return self[var_path]