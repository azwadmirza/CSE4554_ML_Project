    def __call__(self, projectables, optional_datasets=None, **info):
        """Get the emissive part an NIR channel after having derived the reflectance. 
        Not supposed to be used for wavelength outside [3, 4] µm.
        """
        self._init_refl3x(projectables)
        # Derive the sun-zenith angles, and use the nir and thermal ir
        # brightness tempertures and derive the reflectance using
        # PySpectral. The reflectance is stored internally in PySpectral and
        # needs to be derived first in order to get the emissive part.
        _ = self._get_reflectance(projectables, optional_datasets)
        _nir, _ = projectables
        proj = Dataset(self._refl3x.emissive_part_3x(), **_nir.info)

        proj.info['units'] = 'K'
        self.apply_modifier_info(_nir, proj)

        return proj