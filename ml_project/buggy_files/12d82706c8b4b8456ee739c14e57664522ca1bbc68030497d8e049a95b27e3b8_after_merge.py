    def _load_dataset_with_area(self, dsid, coords):
        """Loads *dsid* and it's area if available."""
        file_handlers = self._get_file_handlers(dsid)
        if not file_handlers:
            return

        area = self._load_dataset_area(dsid, file_handlers, coords)
        slice_kwargs, area = self._get_slices(area)

        try:
            ds = self._load_dataset_data(file_handlers, dsid, **slice_kwargs)
        except (KeyError, ValueError) as err:
            logger.exception("Could not load dataset '%s': %s", dsid, str(err))
            return None

        if area is not None:
            ds.attrs['area'] = area
            if (('x' not in ds.coords) or('y' not in ds.coords)) and \
                    hasattr(area, 'get_proj_vectors_dask'):
                ds['x'], ds['y'] = area.get_proj_vectors_dask(CHUNK_SIZE)
        return ds