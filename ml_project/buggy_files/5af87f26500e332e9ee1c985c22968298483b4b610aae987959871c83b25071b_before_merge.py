    def function_nd(self, axis):
        """%s

        """
        x = axis[np.newaxis, :]
        o = self.offset.map['values'][..., np.newaxis]
        return self._function(x, o)