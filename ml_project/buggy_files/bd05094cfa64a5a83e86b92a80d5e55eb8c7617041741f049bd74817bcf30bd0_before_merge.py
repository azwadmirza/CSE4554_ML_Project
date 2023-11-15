    def __getitem__(self, item):
        cls = type(self)
        has_take = hasattr(self._arrow_array, 'take')
        if not self._force_use_pandas and has_take:
            if pd.api.types.is_scalar(item):
                item = item + len(self) if item < 0 else item
                return self._post_scalar_getitem(
                    self._arrow_array.take([item]))
            elif self._can_process_slice_via_arrow(item):
                length = len(self)
                start, stop = item.start, item.stop
                start = self._process_pos(start, length, True)
                stop = self._process_pos(stop, length, False)
                return cls(self._arrow_array.slice(offset=start, length=stop - start),
                           dtype=self._dtype)
            elif hasattr(item, 'dtype') and np.issubdtype(item.dtype, np.bool_):
                return cls(self._arrow_array.filter(pa.array(item, from_pandas=True)),
                           dtype=self._dtype)
            elif hasattr(item, 'dtype'):
                length = len(self)
                item = np.where(item < 0, item + length, item)
                return cls(self._arrow_array.take(item), dtype=self._dtype)

        array = np.asarray(self._arrow_array.to_pandas())
        return cls(array[item], dtype=self._dtype)