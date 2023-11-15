    def _parse_parameter_file(self):
        """Read in metadata describing the overall data on-disk.
        """
        f = self._handle
        bp = self.base_path
        mp = self.meshes_path

        self.unique_identifier = 0
        self.parameters = 0
        self.periodicity = np.zeros(3, dtype=np.bool)
        self.refine_by = 1
        self.cosmological_simulation = 0

        try:
            shapes = {}
            left_edges = {}
            right_edges = {}
            meshes = f[bp + mp]
            for mname in meshes.keys():
                mesh = meshes[mname]
                if type(mesh) is h5.Group:
                    shape = np.asarray(mesh[list(mesh.keys())[0]].shape)
                else:
                    shape = np.asarray(mesh.shape)
                spacing = np.asarray(mesh.attrs["gridSpacing"])
                offset = np.asarray(mesh.attrs["gridGlobalOffset"])
                unit_si = np.asarray(mesh.attrs["gridUnitSI"])
                le = offset * unit_si
                re = le + shape * unit_si * spacing
                shapes[mname] = shape
                left_edges[mname] = le
                right_edges[mname] = re
            lowest_dim = np.min([len(i) for i in shapes.values()])
            shapes = np.asarray([i[:lowest_dim] for i in shapes.values()])
            left_edges = np.asarray([i[:lowest_dim] for i in left_edges.values()])
            right_edges = np.asarray([i[:lowest_dim] for i in right_edges.values()])
            fs = []
            dle = []
            dre = []
            for i in np.arange(lowest_dim):
                fs.append(np.max(shapes.transpose()[i]))
                dle.append(np.min(left_edges.transpose()[i]))
                dre.append(np.min(right_edges.transpose()[i]))
            self.dimensionality = len(fs)
            self.domain_dimensions = np.append(fs, np.ones(3 - self.dimensionality))
            self.domain_left_edge = np.append(dle, np.zeros(3 - len(dle)))
            self.domain_right_edge = np.append(dre, np.ones(3 - len(dre)))
        except(KeyError):
            if self.standard_version <= StrictVersion("1.1.0"):
                self.dimensionality = 3
                self.domain_dimensions = np.ones(3, dtype=np.float64)
                self.domain_left_edge = np.zeros(3, dtype=np.float64)
                self.domain_right_edge = np.ones(3, dtype=np.float64)
            else:
                raise

        self.current_time = f[bp].attrs["time"] * f[bp].attrs["timeUnitSI"]