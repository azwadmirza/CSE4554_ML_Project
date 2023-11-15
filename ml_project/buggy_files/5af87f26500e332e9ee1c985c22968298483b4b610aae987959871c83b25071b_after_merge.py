    def function_nd(self, axis):
        """%s

        """
        if self._is_navigation_multidimensional:
            x = axis[np.newaxis, :]
            o = self.offset.map['values'][..., np.newaxis]
        else:
            x = axis
            o = self.offset.value
        return self._function(x, o)