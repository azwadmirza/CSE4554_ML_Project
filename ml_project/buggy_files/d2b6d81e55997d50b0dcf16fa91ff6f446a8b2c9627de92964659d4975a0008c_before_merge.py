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
            for mesh in f[bp + mp].keys():
                if type(f[bp + mp + mesh]) is h5.Group:
                    shape = np.asarray(f[bp + mp + mesh + "/" + list(f[bp + mp + mesh].keys())[0]].shape)
                else:
                    shapes[mesh] = np.asarray(f[bp + mp + mesh].shape)
                spacing = np.asarray(f[bp + mp + mesh].attrs["gridSpacing"])
                offset = np.asarray(f[bp + mp + mesh].attrs["gridGlobalOffset"])
                unit_si = np.asarray(f[bp + mp + mesh].attrs["gridUnitSI"])
                le = offset * unit_si
                re = le + shape * unit_si * spacing
                shapes[mesh] = shape
                left_edges[mesh] = le
                right_edges[mesh] = re
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
        except ValueError:
            mylog.warning("open_pmd - It seems your data does not contain meshes. Assuming domain extent of 1m^3!")
            self.dimensionality = 3
            self.domain_dimensions = np.ones(3, dtype=np.float64)
            self.domain_left_edge = np.zeros(3, dtype=np.float64)
            self.domain_right_edge = np.ones(3, dtype=np.float64)

        self.current_time = f[bp].attrs["time"] * f[bp].attrs["timeUnitSI"]