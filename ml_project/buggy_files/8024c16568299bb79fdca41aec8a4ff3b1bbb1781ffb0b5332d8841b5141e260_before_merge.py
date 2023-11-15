    def _detect_output_fields(self):
        """Populates ``self.field_list`` with native fields (mesh and particle) on disk.

        Each entry is a tuple of two strings. The first element is the on-disk fluid type or particle type.
        The second element is the name of the field in yt. This string is later used for accessing the data.
        Convention suggests that the on-disk fluid type should be "openPMD",
        the on-disk particle type (for a single species of particles) is "io"
        or (for multiple species of particles) the particle name on-disk.
        """
        f = self.dataset._handle
        bp = self.dataset.base_path
        mp = self.dataset.meshes_path
        pp = self.dataset.particles_path

        mesh_fields = []
        try:
            for field in f[bp + mp].keys():
                try:
                    for axis in f[bp + mp + field].keys():
                        mesh_fields.append(field.replace("_", "-")
                                           + "_" + axis)
                except AttributeError:
                    # This is a h5.Dataset (i.e. no axes)
                    mesh_fields.append(field.replace("_", "-"))
        except KeyError:
            # There are no mesh fields
            pass
        self.field_list = [("openPMD", str(field)) for field in mesh_fields]

        particle_fields = []
        try:
            for species in f[bp + pp].keys():
                for record in f[bp + pp + species].keys():
                    if is_const_component(f[bp + pp + species + "/" + record]):
                        # Record itself (e.g. particle_mass) is constant
                        particle_fields.append(species.replace("_", "-")
                                               + "_" + record.replace("_", "-"))
                    elif "particlePatches" not in record:
                        try:
                            # Create a field for every axis (x,y,z) of every property (position)
                            # of every species (electrons)
                            axes = list(f[bp + pp + species + "/" + record].keys())
                            if str(record) == "position":
                                record = "positionCoarse"
                            for axis in axes:
                                particle_fields.append(species.replace("_", "-")
                                                       + "_" + record.replace("_", "-")
                                                       + "_" + axis)
                        except AttributeError:
                            # Record is a dataset, does not have axes (e.g. weighting)
                            particle_fields.append(species.replace("_", "-")
                                                   + "_" + record.replace("_", "-"))
                            pass
                    else:
                        pass
            if len(list(f[bp + pp].keys())) > 1:
                # There is more than one particle species, use the specific names as field types
                self.field_list.extend(
                    [(str(field).split("_")[0],
                      ("particle_" + "_".join(str(field).split("_")[1:]))) for field in particle_fields])
            else:
                # Only one particle species, fall back to "io"
                self.field_list.extend(
                    [("io",
                      ("particle_" + "_".join(str(field).split("_")[1:]))) for field in particle_fields])
        except KeyError:
            # There are no particle fields
            pass