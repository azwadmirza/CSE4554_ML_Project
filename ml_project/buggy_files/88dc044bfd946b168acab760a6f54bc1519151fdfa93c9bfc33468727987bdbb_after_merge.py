    def function_nd(self, *args):
        """%s

        """
        if self._is2D:
            x, y = args[0], args[1]
            # navigation dimension is 0, f_nd same as f
            if not self._is_navigation_multidimensional:
                return self.function(x, y)
            else:
                return self._f(x[np.newaxis, ...], y[np.newaxis, ...],
                               *[p.map['values'][..., np.newaxis, np.newaxis]
                                 for p in self.parameters])
        else:
            x = args[0]
            if not self._is_navigation_multidimensional:
                return self.function(x)
            else:
                return self._f(x[np.newaxis, ...],
                               *[p.map['values'][..., np.newaxis]
                                 for p in self.parameters])