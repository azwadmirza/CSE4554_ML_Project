    def _count_grids(self):
        """Sets ``self.num_grids`` to be the total number of grids in the simulation.

        The number of grids is determined by their respective memory footprint.
        """
        f = self.dataset._handle
        bp = self.dataset.base_path
        mp = self.dataset.meshes_path
        pp = self.dataset.particles_path

        self.meshshapes = {}
        self.numparts = {}

        self.num_grids = 0

        try:
            meshes = f[bp + mp]
            for mname in meshes.keys():
                mesh = meshes[mname]
                if type(mesh) is h5.Group:
                    shape = mesh[list(mesh.keys())[0]].shape
                else:
                    shape = mesh.shape
                spacing = tuple(mesh.attrs["gridSpacing"])
                offset = tuple(mesh.attrs["gridGlobalOffset"])
                unit_si = mesh.attrs["gridUnitSI"]
                self.meshshapes[mname] = (shape, spacing, offset, unit_si)
        except(KeyError):
            pass

        try:
            particles = f[bp + pp]
            for pname in particles.keys():
                species = particles[pname]
                if "particlePatches" in species.keys():
                    for (patch, size) in enumerate(species["/particlePatches/numParticles"]):
                        self.numparts[pname + "#" + str(patch)] = size
                else:
                    axis = list(species["/position"].keys())[0]
                    if is_const_component(species["/position/" + axis]):
                        self.numparts[pname] = species["/position/" + axis].attrs["shape"]
                    else:
                        self.numparts[pname] = species["/position/" + axis].len()
        except(KeyError):
            pass

        # Limit values per grid by resulting memory footprint
        self.vpg = int(self.dataset.gridsize / 4)  # 4Byte per value (f32)

        # Meshes of the same size do not need separate chunks
        for (shape, spacing, offset, unit_si) in set(self.meshshapes.values()):
            self.num_grids += min(shape[0], int(np.ceil(reduce(mul, shape) * self.vpg**-1)))

        # Same goes for particle chunks if they are not inside particlePatches
        patches = {}
        no_patches = {}
        for (k, v) in self.numparts.items():
            if "#" in k:
                patches[k] = v
            else:
                no_patches[k] = v
        for size in set(no_patches.values()):
            self.num_grids += int(np.ceil(size * self.vpg**-1))
        for size in patches.values():
            self.num_grids += int(np.ceil(size * self.vpg**-1))