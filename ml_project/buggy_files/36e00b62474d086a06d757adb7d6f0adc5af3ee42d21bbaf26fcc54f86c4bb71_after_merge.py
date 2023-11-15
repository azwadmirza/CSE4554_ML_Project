    def __init__(self, boundaries, ncolors, clip=False, *, extend='neither'):
        """
        Parameters
        ----------
        boundaries : array-like
            Monotonically increasing sequence of at least 2 boundaries.
        ncolors : int
            Number of colors in the colormap to be used.
        clip : bool, optional
            If clip is ``True``, out of range values are mapped to 0 if they
            are below ``boundaries[0]`` or mapped to ``ncolors - 1`` if they
            are above ``boundaries[-1]``.

            If clip is ``False``, out of range values are mapped to -1 if
            they are below ``boundaries[0]`` or mapped to *ncolors* if they are
            above ``boundaries[-1]``. These are then converted to valid indices
            by `Colormap.__call__`.
        extend : {'neither', 'both', 'min', 'max'}, default: 'neither'
            Extend the number of bins to include one or both of the
            regions beyond the boundaries.  For example, if ``extend``
            is 'min', then the color to which the region between the first
            pair of boundaries is mapped will be distinct from the first
            color in the colormap, and by default a
            `~matplotlib.colorbar.Colorbar` will be drawn with
            the triangle extension on the left or lower end.

        Returns
        -------
        int16 scalar or array

        Notes
        -----
        *boundaries* defines the edges of bins, and data falling within a bin
        is mapped to the color with the same index.

        If the number of bins, including any extensions, is less than
        *ncolors*, the color index is chosen by linear interpolation, mapping
        the ``[0, nbins - 1]`` range onto the ``[0, ncolors - 1]`` range.
        """
        if clip and extend != 'neither':
            raise ValueError("'clip=True' is not compatible with 'extend'")
        self.clip = clip
        self.vmin = boundaries[0]
        self.vmax = boundaries[-1]
        self.boundaries = np.asarray(boundaries)
        self.N = len(self.boundaries)
        if self.N < 2:
            raise ValueError("You must provide at least 2 boundaries "
                             f"(1 region) but you passed in {boundaries!r}")
        self.Ncmap = ncolors
        self.extend = extend

        self._n_regions = self.N - 1  # number of colors needed
        self._offset = 0
        if extend in ('min', 'both'):
            self._n_regions += 1
            self._offset = 1
        if extend in ('max', 'both'):
            self._n_regions += 1
        if self._n_regions > self.Ncmap:
            raise ValueError(f"There are {self._n_regions} color bins "
                             "including extensions, but ncolors = "
                             f"{ncolors}; ncolors must equal or exceed the "
                             "number of bins")