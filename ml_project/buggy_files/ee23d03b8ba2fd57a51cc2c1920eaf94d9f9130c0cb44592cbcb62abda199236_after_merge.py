    def copy(self):
        if self._use_arrow:
            return type(self)(copy_obj(self._arrow_array))
        else:
            return type(self)(self._ndarray.copy())