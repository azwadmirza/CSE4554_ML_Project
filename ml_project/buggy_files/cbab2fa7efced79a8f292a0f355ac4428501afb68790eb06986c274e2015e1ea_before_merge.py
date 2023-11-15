    def plot_ephem(self, ephem, epoch=None, *, label=None, color=None, trail=False):
        """Plots Ephem object over its sampling period.

        Parameters
        ----------
        ephem : ~poliastro.ephem.Ephem
            Ephemerides to plot.
        epoch : astropy.time.Time, optional
            Epoch of the current position, none will be used if not given.
        label : str, optional
            Label of the orbit, default to the name of the body.
        color : string, optional
            Color of the line and the position.
        trail : bool, optional
            Fade the orbit trail, default to False.

        """
        super().plot_ephem(ephem, epoch, label=label, color=color, trail=trail)

        if not self._figure._in_batch_mode:
            return self.show()