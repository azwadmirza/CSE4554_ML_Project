    def __init__(
        self, data, *,
        hue=None, hue_order=None, palette=None,
        hue_kws=None, vars=None, x_vars=None, y_vars=None,
        corner=False, diag_sharey=True, height=2.5, aspect=1,
        layout_pad=.5, despine=True, dropna=False, size=None
    ):
        """Initialize the plot figure and PairGrid object.

        Parameters
        ----------
        data : DataFrame
            Tidy (long-form) dataframe where each column is a variable and
            each row is an observation.
        hue : string (variable name)
            Variable in ``data`` to map plot aspects to different colors. This
            variable will be excluded from the default x and y variables.
        hue_order : list of strings
            Order for the levels of the hue variable in the palette
        palette : dict or seaborn color palette
            Set of colors for mapping the ``hue`` variable. If a dict, keys
            should be values  in the ``hue`` variable.
        hue_kws : dictionary of param -> list of values mapping
            Other keyword arguments to insert into the plotting call to let
            other plot attributes vary across levels of the hue variable (e.g.
            the markers in a scatterplot).
        vars : list of variable names
            Variables within ``data`` to use, otherwise use every column with
            a numeric datatype.
        {x, y}_vars : lists of variable names
            Variables within ``data`` to use separately for the rows and
            columns of the figure; i.e. to make a non-square plot.
        corner : bool
            If True, don't add axes to the upper (off-diagonal) triangle of the
            grid, making this a "corner" plot.
        height : scalar
            Height (in inches) of each facet.
        aspect : scalar
            Aspect * height gives the width (in inches) of each facet.
        layout_pad : scalar
            Padding between axes; passed to ``fig.tight_layout``.
        despine : boolean
            Remove the top and right spines from the plots.
        dropna : boolean
            Drop missing values from the data before plotting.

        See Also
        --------
        pairplot : Easily drawing common uses of :class:`PairGrid`.
        FacetGrid : Subplot grid for plotting conditional relationships.

        Examples
        --------

        .. include:: ../docstrings/PairGrid.rst

        """

        super(PairGrid, self).__init__()

        # Handle deprecations
        if size is not None:
            height = size
            msg = ("The `size` parameter has been renamed to `height`; "
                   "please update your code.")
            warnings.warn(UserWarning(msg))

        # Sort out the variables that define the grid
        numeric_cols = self._find_numeric_cols(data)
        if hue in numeric_cols:
            numeric_cols.remove(hue)
        if vars is not None:
            x_vars = list(vars)
            y_vars = list(vars)
        if x_vars is None:
            x_vars = numeric_cols
        if y_vars is None:
            y_vars = numeric_cols

        if np.isscalar(x_vars):
            x_vars = [x_vars]
        if np.isscalar(y_vars):
            y_vars = [y_vars]

        self.x_vars = x_vars = list(x_vars)
        self.y_vars = y_vars = list(y_vars)
        self.square_grid = self.x_vars == self.y_vars

        if not x_vars:
            raise ValueError("No variables found for grid columns.")
        if not y_vars:
            raise ValueError("No variables found for grid rows.")

        # Create the figure and the array of subplots
        figsize = len(x_vars) * height * aspect, len(y_vars) * height

        fig, axes = plt.subplots(len(y_vars), len(x_vars),
                                 figsize=figsize,
                                 sharex="col", sharey="row",
                                 squeeze=False)

        # Possibly remove upper axes to make a corner grid
        # Note: setting up the axes is usually the most time-intensive part
        # of using the PairGrid. We are foregoing the speed improvement that
        # we would get by just not setting up the hidden axes so that we can
        # avoid implementing plt.subplots ourselves. But worth thinking about.
        self._corner = corner
        if corner:
            hide_indices = np.triu_indices_from(axes, 1)
            for i, j in zip(*hide_indices):
                axes[i, j].remove()
                axes[i, j] = None

        self.fig = fig
        self.axes = axes
        self.data = data

        # Save what we are going to do with the diagonal
        self.diag_sharey = diag_sharey
        self.diag_vars = None
        self.diag_axes = None

        self._dropna = dropna

        # Label the axes
        self._add_axis_labels()

        # Sort out the hue variable
        self._hue_var = hue
        if hue is None:
            self.hue_names = hue_order = ["_nolegend_"]
            self.hue_vals = pd.Series(["_nolegend_"] * len(data),
                                      index=data.index)
        else:
            # We need hue_order and hue_names because the former is used to control
            # the order of drawing and the latter is used to control the order of
            # the legend. hue_names can become string-typed while hue_order must
            # retain the type of the input data. This is messy but results from
            # the fact that PairGrid can implement the hue-mapping logic itself
            # (and was originally written exclusively that way) but now can delegate
            # to the axes-level functions, while always handling legend creation.
            # See GH2307
            hue_names = hue_order = categorical_order(data[hue], hue_order)
            if dropna:
                # Filter NA from the list of unique hue names
                hue_names = list(filter(pd.notnull, hue_names))
            self.hue_names = hue_names
            self.hue_vals = data[hue]

        # Additional dict of kwarg -> list of values for mapping the hue var
        self.hue_kws = hue_kws if hue_kws is not None else {}

        self._orig_palette = palette
        self._hue_order = hue_order
        self.palette = self._get_palette(data, hue, hue_order, palette)
        self._legend_data = {}

        # Make the plot look nice
        self._tight_layout_rect = [.01, .01, .99, .99]
        self._tight_layout_pad = layout_pad
        self._despine = despine
        if despine:
            utils.despine(fig=fig)
        self.tight_layout(pad=layout_pad)