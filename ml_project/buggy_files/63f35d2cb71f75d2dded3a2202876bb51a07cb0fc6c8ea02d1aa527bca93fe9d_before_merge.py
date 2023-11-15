    def map(self, func, *args, **kwargs):
        """
        Apply a plotting function to each facet's subset of the data.

        Parameters
        ----------
        func : callable
            A plotting function that takes data and keyword arguments. It
            must plot to the currently active matplotlib Axes and take a
            `color` keyword argument. If faceting on the `hue` dimension,
            it must also take a `label` keyword argument.
        args : strings
            Column names in self.data that identify variables with data to
            plot. The data for each variable is passed to `func` in the
            order the variables are specified in the call.
        kwargs : keyword arguments
            All keyword arguments are passed to the plotting function.

        Returns
        -------
        self : FacetGrid object

        """
        import matplotlib.pyplot as plt

        for ax, namedict in zip(self.axes.flat, self.name_dicts.flat):
            if namedict is not None:
                data = self.data.loc[namedict]
                plt.sca(ax)
                innerargs = [data[a].values for a in args]
                # TODO: is it possible to verify that an artist is mappable?
                mappable = func(*innerargs, **kwargs)
                self._mappables.append(mappable)

        self._finalize_grid(*args[:2])

        return self