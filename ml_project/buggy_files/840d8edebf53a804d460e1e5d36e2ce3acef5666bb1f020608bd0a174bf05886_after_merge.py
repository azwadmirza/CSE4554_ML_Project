    def _parse_index(self):
        """Fills each grid with appropriate properties (extent, dimensions, ...)

        This calculates the properties of every OpenPMDGrid based on the total number of grids in the simulation.
        The domain is divided into ``self.num_grids`` (roughly) equally sized chunks along the x-axis.
        ``grid_levels`` is always equal to 0 since we only have one level of refinement in openPMD.

        Notes
        -----
        ``self.grid_dimensions`` is rounded to the nearest integer. Grid edges are calculated from this dimension.
        Grids with dimensions [0, 0, 0] are particle only. The others do not have any particles affiliated with them.
        """
        f = self.dataset._handle
        bp = self.dataset.base_path
        pp = self.dataset.particles_path

        self.grid_levels.flat[:] = 0
        self.grids = np.empty(self.num_grids, dtype="object")

        grid_index_total = 0

        # Mesh grids
        for mesh in set(self.meshshapes.values()):
            (shape, spacing, offset, unit_si) = mesh
            shape = np.asarray(shape)
            spacing = np.asarray(spacing)
            offset = np.asarray(offset)
            # Total dimension of this grid
            domain_dimension = np.asarray(shape, dtype=np.int32)
            domain_dimension = np.append(domain_dimension, np.ones(3 - len(domain_dimension)))
            # Number of grids of this shape
            num_grids = min(shape[0], int(np.ceil(reduce(mul, shape) * self.vpg**-1)))
            gle = offset * unit_si  # self.dataset.domain_left_edge
            gre = domain_dimension[:spacing.size] * unit_si * spacing + gle  # self.dataset.domain_right_edge
            gle = np.append(gle, np.zeros(3 - len(gle)))
            gre = np.append(gre, np.ones(3 - len(gre)))
            grid_dim_offset = np.linspace(0, domain_dimension[0], num_grids + 1, dtype=np.int32)
            grid_edge_offset = grid_dim_offset * np.float(domain_dimension[0])**-1 * (gre[0] - gle[0]) + gle[0]
            mesh_names = []
            for (mname, mdata) in self.meshshapes.items():
                if mesh == mdata:
                    mesh_names.append(str(mname))
            prev = 0
            for grid in np.arange(num_grids):
                self.grid_dimensions[grid_index_total] = domain_dimension
                self.grid_dimensions[grid_index_total][0] = grid_dim_offset[grid + 1] - grid_dim_offset[grid]
                self.grid_left_edge[grid_index_total] = gle
                self.grid_left_edge[grid_index_total][0] = grid_edge_offset[grid]
                self.grid_right_edge[grid_index_total] = gre
                self.grid_right_edge[grid_index_total][0] = grid_edge_offset[grid + 1]
                self.grid_particle_count[grid_index_total] = 0
                self.grids[grid_index_total] = self.grid(grid_index_total, self, 0,
                                                         fi=prev,
                                                         fo=self.grid_dimensions[grid_index_total][0],
                                                         ft=mesh_names)
                prev += self.grid_dimensions[grid_index_total][0]
                grid_index_total += 1

        handled_ptypes = []

        # Particle grids
        for (species, count) in self.numparts.items():
            if "#" in species:
                # This is a particlePatch
                spec = species.split("#")
                patch = f[bp + pp + "/" + spec[0] + "/particlePatches"]
                domain_dimension = np.ones(3, dtype=np.int32)
                for (ind, axis) in enumerate(list(patch["extent"].keys())):
                    domain_dimension[ind] = patch["extent/" + axis].value[int(spec[1])]
                num_grids = int(np.ceil(count * self.vpg**-1))
                gle = []
                for axis in patch["offset"].keys():
                    gle.append(get_component(patch, "offset/" + axis, int(spec[1]), 1)[0])
                gle = np.asarray(gle)
                gle = np.append(gle, np.zeros(3 - len(gle)))
                gre = []
                for axis in patch["extent"].keys():
                    gre.append(get_component(patch, "extent/" + axis, int(spec[1]), 1)[0])
                gre = np.asarray(gre)
                gre = np.append(gre, np.ones(3 - len(gre)))
                np.add(gle, gre, gre)
                npo = patch["numParticlesOffset"].value.item(int(spec[1]))
                particle_count = np.linspace(npo, npo + count, num_grids + 1,
                                             dtype=np.int32)
                particle_names = [str(spec[0])]
            elif str(species) not in handled_ptypes:
                domain_dimension = self.dataset.domain_dimensions
                num_grids = int(np.ceil(count * self.vpg**-1))
                gle = self.dataset.domain_left_edge
                gre = self.dataset.domain_right_edge
                particle_count = np.linspace(0, count, num_grids + 1, dtype=np.int32)
                particle_names = []
                for (pname, size) in self.numparts.items():
                    if size == count:
                        # Since this is not part of a particlePatch, we can include multiple same-sized ptypes
                        particle_names.append(str(pname))
                        handled_ptypes.append(str(pname))
            else:
                # A grid with this exact particle count has already been created
                continue
            for grid in np.arange(num_grids):
                self.grid_dimensions[grid_index_total] = domain_dimension
                self.grid_left_edge[grid_index_total] = gle
                self.grid_right_edge[grid_index_total] = gre
                self.grid_particle_count[grid_index_total] = (particle_count[grid + 1] - particle_count[grid]) * len(
                    particle_names)
                self.grids[grid_index_total] = self.grid(grid_index_total, self, 0,
                                                         pi=particle_count[grid],
                                                         po=particle_count[grid + 1] - particle_count[grid],
                                                         pt=particle_names)
                grid_index_total += 1