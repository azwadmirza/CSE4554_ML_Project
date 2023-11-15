    def _get_reflectance(self, projectables, optional_datasets):
        """Calculate 3.x reflectance with pyspectral"""
        _nir, _tb11 = projectables
        LOG.info('Getting reflective part of %s', _nir.attrs['name'])

        sun_zenith = None
        tb13_4 = None

        for dataset in optional_datasets:
            if (dataset.attrs['units'] == 'K' and
                    "wavelengh" in dataset.attrs and
                    dataset.attrs["wavelength"][0] <= 13.4 <= dataset.attrs["wavelength"][2]):
                tb13_4 = dataset
            elif dataset.attrs["standard_name"] == "solar_zenith_angle":
                sun_zenith = dataset

        # Check if the sun-zenith angle was provided:
        if sun_zenith is None:
            from pyorbital.astronomy import sun_zenith_angle as sza
            lons, lats = _nir.attrs["area"].get_lonlats_dask(CHUNK_SIZE)
            sun_zenith = sza(_nir.attrs['start_time'], lons, lats)

        return self._refl3x.reflectance_from_tbs(sun_zenith, _nir, _tb11, tb_ir_co2=tb13_4)