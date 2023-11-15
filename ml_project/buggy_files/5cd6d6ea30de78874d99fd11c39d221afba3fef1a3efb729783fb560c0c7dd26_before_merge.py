    def __init__(self, initialdata=None, **kwargs):
        """Make a CRS from a PROJ dict or mapping

        Parameters
        ----------
        initialdata : mapping, optional
            A dictionary or other mapping
        kwargs : mapping, optional
            Another mapping. Will be overlaid on the initialdata.

        Returns
        -------
        CRS

        """
        self._wkt = None
        self._data = None
        self._crs = None

        if initialdata or kwargs:

            data = dict(initialdata or {})
            data.update(**kwargs)
            data = {k: v for k, v in data.items() if k in all_proj_keys}

            # always use lowercase 'epsg'.
            if 'init' in data:
                data['init'] = data['init'].replace('EPSG:', 'epsg:')

            proj = ' '.join(['+{}={}'.format(key, val) for key, val in data.items()])
            self._crs = _CRS.from_proj4(proj)

        else:
            self._crs = _CRS()