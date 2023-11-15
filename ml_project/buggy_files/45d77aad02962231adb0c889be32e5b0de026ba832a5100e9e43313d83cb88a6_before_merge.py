    def _get_particle_type_counts(self):
        """Reads the active number of particles for every species.

        Returns
        -------
        dict
            keys are ptypes
            values are integer counts of the ptype
        """
        result = {}
        f = self.dataset._handle
        bp = self.dataset.base_path
        pp = self.dataset.particles_path
        for ptype in self.ds.particle_types_raw:
            if str(ptype) == "io":
                spec = list(f[bp + pp].keys())[0]
            else:
                spec = ptype
            axis = list(f[bp + pp + "/" + spec + "/position"].keys())[0]
            pos = f[bp + pp + "/" + spec + "/position/" + axis]
            if is_const_component(pos):
                result[ptype] = pos.attrs["shape"]
            else:
                result[ptype] = pos.len()
        return result