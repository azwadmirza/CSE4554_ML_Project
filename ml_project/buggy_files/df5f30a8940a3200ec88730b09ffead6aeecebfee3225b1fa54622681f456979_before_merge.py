    def swap_axes(self, swap_axes: Optional[bool] = True):
        """
        Plots a transposed image.

        By default, the x axis contains `var_names` (e.g. genes) and the y
        axis the `groupby` categories. By setting `swap_axes` then x are
        the `groupby` categories and y the `var_names`.

        Parameters
        ----------
        swap_axes : bool, default: True

        Returns
        -------
        BasePlot

        """
        self.DEFAULT_CATEGORY_HEIGHT, self.DEFAULT_CATEGORY_WIDTH = (
            self.DEFAULT_CATEGORY_WIDTH,
            self.DEFAULT_CATEGORY_HEIGHT,
        )

        self.are_axes_swapped = swap_axes
        return self