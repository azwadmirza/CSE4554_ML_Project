    def __init__(self, data, header, plot_settings=None, **kwargs):

        # If the data has more than two dimensions, the first dimensions
        # (NAXIS1, NAXIS2) are used and the rest are discarded.
        ndim = data.ndim
        if ndim > 2:
            # We create a slice that removes all but the 'last' two
            # dimensions. (Note dimensions in ndarray are in reverse order)

            new_2d_slice = [0]*(ndim-2)
            new_2d_slice.extend([slice(None), slice(None)])
            data = data[new_2d_slice]
            # Warn the user that the data has been truncated
            warnings.warn_explicit("This file contains more than 2 dimensions. "
                                   "Only the first two dimensions will be used."
                                   " The truncated data will not be saved in a new file.",
                                   Warning, __file__, inspect.currentframe().f_back.f_lineno)

        super(GenericMap, self).__init__(data, meta=header, **kwargs)

        # Correct possibly missing meta keywords
        self._fix_date()
        self._fix_naxis()

        # Setup some attributes
        self._nickname = None

        # Validate header
        # TODO: This should be a function of the header, not of the map
        self._validate_meta()
        self._shift = SpatialPair(0 * u.arcsec, 0 * u.arcsec)

        if self.dtype == np.uint8:
            norm = None
        else:
            norm = colors.Normalize()

        # Visualization attributes
        self.plot_settings = {'cmap': cm.gray,
                              'norm': norm,
                              'interpolation': 'nearest',
                              'origin': 'lower'
                              }
        if plot_settings:
            self.plot_settings.update(plot_settings)