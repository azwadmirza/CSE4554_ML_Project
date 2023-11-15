    def __init__(self, data, header, plot_settings=None, **kwargs):

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