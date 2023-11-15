    def _init_refl3x(self, projectables):
        """Initiate the 3.x reflectance derivations
        """
        try:
            from pyspectral.near_infrared_reflectance import Calculator
        except ImportError:
            LOG.info("Couldn't load pyspectral")
            raise

        _nir, _tb11 = projectables
        self._refl3x = Calculator(_nir.attrs['platform_name'], _nir.attrs['sensor'], _nir.attrs['name'])