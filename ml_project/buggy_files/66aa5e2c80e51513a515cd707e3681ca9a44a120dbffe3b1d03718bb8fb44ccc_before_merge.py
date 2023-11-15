    def __init__(self, data, col=None, row=None, col_wrap=None,
                 sharex=True, sharey=True, figsize=None, aspect=1, size=3,
                 subplot_kws=None):
        """
        Parameters
        ----------
        data : DataArray
            xarray DataArray to be plotted
        row, col : strings
            Dimesion names that define subsets of the data, which will be drawn
            on separate facets in the grid.
        col_wrap : int, optional
            "Wrap" the column variable at this width, so that the column facets
        sharex : bool, optional
            If true, the facets will share x axes
        sharey : bool, optional
            If true, the facets will share y axes
        figsize : tuple, optional
            A tuple (width, height) of the figure in inches.
            If set, overrides ``size`` and ``aspect``.
        aspect : scalar, optional
            Aspect ratio of each facet, so that ``aspect * size`` gives the
            width of each facet in inches
        size : scalar, optional
            Height (in inches) of each facet. See also: ``aspect``
        subplot_kws : dict, optional
            Dictionary of keyword arguments for matplotlib subplots

        """

        import matplotlib.pyplot as plt

        # Handle corner case of nonunique coordinates
        rep_col = col is not None and not data[col].to_index().is_unique
        rep_row = row is not None and not data[row].to_index().is_unique
        if rep_col or rep_row:
            raise ValueError('Coordinates used for faceting cannot '
                             'contain repeated (nonunique) values.')

        # single_group is the grouping variable, if there is exactly one
        if col and row:
            single_group = False
            nrow = len(data[row])
            ncol = len(data[col])
            nfacet = nrow * ncol
            if col_wrap is not None:
                warnings.warn('Ignoring col_wrap since both col and row '
                              'were passed')
        elif row and not col:
            single_group = row
        elif not row and col:
            single_group = col
        else:
            raise ValueError(
                'Pass a coordinate name as an argument for row or col')

        # Compute grid shape
        if single_group:
            nfacet = len(data[single_group])
            if col:
                # idea - could add heuristic for nice shapes like 3x4
                ncol = nfacet
            if row:
                ncol = 1
            if col_wrap is not None:
                # Overrides previous settings
                ncol = col_wrap
            nrow = int(np.ceil(nfacet / ncol))

        # Set the subplot kwargs
        subplot_kws = {} if subplot_kws is None else subplot_kws

        if figsize is None:
            # Calculate the base figure size with extra horizontal space for a
            # colorbar
            cbar_space = 1
            figsize = (ncol * size * aspect + cbar_space, nrow * size)

        fig, axes = plt.subplots(nrow, ncol,
                                 sharex=sharex, sharey=sharey, squeeze=False,
                                 figsize=figsize, subplot_kw=subplot_kws)

        # Set up the lists of names for the row and column facet variables
        col_names = list(data[col].values) if col else []
        row_names = list(data[row].values) if row else []

        if single_group:
            full = [{single_group: x} for x in
                    data[single_group].values]
            empty = [None for x in range(nrow * ncol - len(full))]
            name_dicts = full + empty
        else:
            rowcols = itertools.product(row_names, col_names)
            name_dicts = [{row: r, col: c} for r, c in rowcols]

        name_dicts = np.array(name_dicts).reshape(nrow, ncol)

        # Set up the class attributes
        # ---------------------------

        # First the public API
        self.data = data
        self.name_dicts = name_dicts
        self.fig = fig
        self.axes = axes
        self.row_names = row_names
        self.col_names = col_names

        # Next the private variables
        self._single_group = single_group
        self._nrow = nrow
        self._row_var = row
        self._ncol = ncol
        self._col_var = col
        self._col_wrap = col_wrap
        self._x_var = None
        self._y_var = None
        self._cmap_extend = None
        self._mappables = []