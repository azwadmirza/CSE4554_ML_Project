    def _init(self):
        """
        Initialization delayed until first draw;
        allow time for axes setup.
        """
        # It seems that there are not enough event notifications
        # available to have this work on an as-needed basis at present.
        if True:  # not self._initialized:
            trans = self._set_transform()
            ax = self.ax
            sx, sy = trans.inverted().transform_point(
                                            (ax.bbox.width, ax.bbox.height))
            self.span = sx
            if self.width is None:
                sn = max(8, min(25, math.sqrt(self.N)))
                self.width = 0.06 * self.span / sn