    def _autolev(self, N):
        """
        Select contour levels to span the data.

        We need two more levels for filled contours than for
        line contours, because for the latter we need to specify
        the lower and upper boundary of each range. For example,
        a single contour boundary, say at z = 0, requires only
        one contour line, but two filled regions, and therefore
        three levels to provide boundaries for both regions.
        """
        if self.locator is None:
            if self.logscale:
                self.locator = ticker.LogLocator()
            else:
                self.locator = ticker.MaxNLocator(N + 1)
        zmax = self.zmax
        zmin = self.zmin
        lev = self.locator.tick_values(zmin, zmax)
        self._auto = True
        if self.filled:
            return lev
        # For line contours, drop levels outside the data range.
        return lev[(lev > zmin) & (lev < zmax)]