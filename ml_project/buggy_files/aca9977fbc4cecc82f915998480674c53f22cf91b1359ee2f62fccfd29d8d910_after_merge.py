    def __call__(self, shape=None, chunk_size=None, inp=None, name=None,
                 names=None):
        if inp is None:
            # create from pandas Index
            name = name if name is not None else self._data.name
            names = names if names is not None else self._data.names
            return self.new_index(None, shape=shape, dtype=self._dtype,
                                  index_value=parse_index(self._data),
                                  name=name, names=names, raw_chunk_size=chunk_size)
        elif hasattr(inp, 'index_value'):
            # get index from Mars DataFrame, Series or Index
            name = name if name is not None else inp.index_value.name
            names = names if names is not None else [name]
            if inp.index_value.has_value():
                self._data = data = inp.index_value.to_pandas()
                return self.new_index(None, shape=(inp.shape[0],), dtype=data.dtype,
                                      index_value=parse_index(data), name=name,
                                      names=names, raw_chunk_size=chunk_size)
            else:
                if self._dtype is None:
                    self._dtype = inp.index_value.to_pandas().dtype
                return self.new_index([inp], shape=(inp.shape[0],),
                                      dtype=self._dtype, index_value=inp.index_value,
                                      name=name, names=names)
        else:
            if inp.ndim != 1:
                raise ValueError('Index data must be 1-dimensional')
            # get index from tensor
            dtype = inp.dtype if self._dtype is None else self._dtype
            pd_index = pd.Index([], dtype=dtype)
            if self._dtype is None:
                self._dtype = pd_index.dtype
            return self.new_index([inp], shape=inp.shape, dtype=self._dtype,
                                  index_value=parse_index(pd_index, inp),
                                  name=name, names=names)