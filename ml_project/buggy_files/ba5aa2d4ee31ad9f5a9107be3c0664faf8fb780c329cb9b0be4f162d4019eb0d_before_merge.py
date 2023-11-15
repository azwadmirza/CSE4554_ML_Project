    def _contour_level_args(self, z, args):
        """
        Determine the contour levels and store in self.levels.
        """
        if self.filled:
            fn = 'contourf'
        else:
            fn = 'contour'
        self._auto = False
        if self.levels is None:
            if len(args) == 0:
                lev = self._autolev(z, 7)
            else:
                level_arg = args[0]
                try:
                    if type(level_arg) == int:
                        lev = self._autolev(z, level_arg)
                    else:
                        lev = np.asarray(level_arg).astype(np.float64)
                except:
                    raise TypeError(
                        "Last %s arg must give levels; see help(%s)" %
                        (fn, fn))
            self.levels = lev
        if self.filled and len(self.levels) < 2:
            raise ValueError("Filled contours require at least 2 levels.")

        if len(self.levels) > 1 and np.amin(np.diff(self.levels)) <= 0.0:
            if hasattr(self, '_corner_mask') and self._corner_mask == 'legacy':
                warnings.warn("Contour levels are not increasing")
            else:
                raise ValueError("Contour levels must be increasing")