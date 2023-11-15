    def copy(self):
        return type(self)(copy_obj(self._arrow_array))