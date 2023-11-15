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

        for mesh in f[bp + mp].keys():
            if type(f[bp + mp + mesh]) is h5.Group:
                shape = f[bp + mp + mesh + "/" + list(f[bp + mp + mesh].keys())[0]].shape
            else:
                shape = f[bp + mp + mesh].shape
            spacing = tuple(f[bp + mp + mesh].attrs["gridSpacing"])
            offset = tuple(f[bp + mp + mesh].attrs["gridGlobalOffset"])
            unit_si = f[bp + mp + mesh].attrs["gridUnitSI"]
            self.meshshapes[mesh] = (shape, spacing, offset, unit_si)
        for species in f[bp + pp].keys():
            if "particlePatches" in f[bp + pp + "/" + species].keys():
                for (patch, size) in enumerate(f[bp + pp + "/" + species + "/particlePatches/numParticles"]):
                    self.numparts[species + "#" + str(patch)] = size
            else:
                axis = list(f[bp + pp + species + "/position"].keys())[0]
                if is_const_component(f[bp + pp + species + "/position/" + axis]):
                    self.numparts[species] = f[bp + pp + species + "/position/" + axis].attrs["shape"]
                else:
                    self.numparts[species] = f[bp + pp + species + "/position/" + axis].len()

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
            self.num_grids += int(np.ceil(size * self.vpg ** -1))
        for size in patches.values():
            self.num_grids += int(np.ceil(size * self.vpg ** -1))