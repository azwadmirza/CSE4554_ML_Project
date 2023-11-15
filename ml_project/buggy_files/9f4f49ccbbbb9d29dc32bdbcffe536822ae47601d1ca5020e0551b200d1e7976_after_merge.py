    def __init__(self,
                 filename,
                 dataset_type="openPMD",
                 storage_filename=None,
                 units_override=None,
                 unit_system="mks",
                 **kwargs):
        self._handle = HDF5FileHandler(filename)
        self.gridsize = kwargs.pop("open_pmd_virtual_gridsize", 10**9)
        self.standard_version = StrictVersion(self._handle.attrs["openPMD"].decode())
        self.iteration = kwargs.pop("iteration", None)
        self._set_paths(self._handle, path.dirname(filename), self.iteration)
        Dataset.__init__(self,
                         filename,
                         dataset_type,
                         units_override=units_override,
                         unit_system=unit_system)
        self.storage_filename = storage_filename
        self.fluid_types += ("openPMD",)
        try:
            particles = tuple(str(c) for c in self._handle[self.base_path + self.particles_path].keys())
            if len(particles) > 1:
                # Only use on-disk particle names if there is more than one species
                self.particle_types = particles
            mylog.debug("self.particle_types: {}".format(self.particle_types))
            self.particle_types_raw = self.particle_types
            self.particle_types = tuple(self.particle_types)
        except(KeyError):
            pass