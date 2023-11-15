    def _parse_parameter_file(self):
        # hardcoded for now
        # These should be explicitly obtained from the file, but for now that
        # will wait until a reorganization of the source tree and better
        # generalization.
        self.dimensionality = 3
        self.refine_by = 2
        self.parameters["HydroMethod"] = "ramses"
        self.parameters["Time"] = 1.0  # default unit is 1...

        # We now execute the same logic Oliver's code does
        rheader = {}

        def read_rhs(f, cast):
            line = f.readline().replace("\n", "")
            p, v = line.split("=")
            rheader[p.strip()] = cast(v.strip())

        with open(self.parameter_filename) as f:
            for _ in range(6):
                read_rhs(f, int)
            f.readline()
            for _ in range(11):
                read_rhs(f, float)
            f.readline()
            read_rhs(f, str)
            # This next line deserves some comment.  We specify a min_level that
            # corresponds to the minimum level in the RAMSES simulation.  RAMSES is
            # one-indexed, but it also does refer to the *oct* dimensions -- so
            # this means that a levelmin of 1 would have *1* oct in it.  So a
            # levelmin of 2 would have 8 octs at the root mesh level.
            self.min_level = rheader["levelmin"] - 1
            # Now we read the hilbert indices
            self.hilbert_indices = {}
            if rheader["ordering type"] == "hilbert":
                f.readline()  # header
                for _ in range(rheader["ncpu"]):
                    dom, mi, ma = f.readline().split()
                    self.hilbert_indices[int(dom)] = (float(mi), float(ma))

        if rheader["ordering type"] != "hilbert" and self._bbox is not None:
            raise NotImplementedError(
                "The ordering %s is not compatible with the `bbox` argument."
                % rheader["ordering type"]
            )
        self.parameters.update(rheader)
        self.domain_left_edge = np.zeros(3, dtype="float64")
        self.domain_dimensions = np.ones(3, dtype="int32") * 2 ** (self.min_level + 1)
        self.domain_right_edge = np.ones(3, dtype="float64")
        # This is likely not true, but it's not clear
        # how to determine the boundary conditions
        self.periodicity = (True, True, True)

        if self.force_cosmological is not None:
            is_cosmological = self.force_cosmological
        else:
            # These conditions seem to always be true for non-cosmological datasets
            is_cosmological = not (
                rheader["time"] >= 0 and rheader["H0"] == 1 and rheader["aexp"] == 1
            )

        if not is_cosmological:
            self.cosmological_simulation = 0
            self.current_redshift = 0
            self.hubble_constant = 0
            self.omega_matter = 0
            self.omega_lambda = 0
        else:
            self.cosmological_simulation = 1
            self.current_redshift = (1.0 / rheader["aexp"]) - 1.0
            self.omega_lambda = rheader["omega_l"]
            self.omega_matter = rheader["omega_m"]
            self.hubble_constant = rheader["H0"] / 100.0  # This is H100

        force_max_level, convention = self._force_max_level
        if convention == "yt":
            force_max_level += self.min_level + 1
        self.max_level = min(force_max_level, rheader["levelmax"]) - self.min_level - 1

        if self.cosmological_simulation == 0:
            self.current_time = self.parameters["time"]
        else:
            self.tau_frw, self.t_frw, self.dtau, self.n_frw, self.time_tot = friedman(
                self.omega_matter,
                self.omega_lambda,
                1.0 - self.omega_matter - self.omega_lambda,
            )

            age = self.parameters["time"]
            iage = 1 + int(10.0 * age / self.dtau)
            iage = np.min([iage, self.n_frw // 2 + (iage - self.n_frw // 2) // 10])

            try:
                self.time_simu = self.t_frw[iage] * (age - self.tau_frw[iage - 1]) / (
                    self.tau_frw[iage] - self.tau_frw[iage - 1]
                ) + self.t_frw[iage - 1] * (age - self.tau_frw[iage]) / (
                    self.tau_frw[iage - 1] - self.tau_frw[iage]
                )

                self.current_time = (
                    (self.time_tot + self.time_simu)
                    / (self.hubble_constant * 1e7 / 3.08e24)
                    / self.parameters["unit_t"]
                )
            except IndexError:
                mylog.warning(
                    "Yt could not convert conformal time to physical time. "
                    "Yt will assume the simulation is *not* cosmological."
                )
                self.cosmological_simulation = 0
                self.current_time = self.parameters["time"]

        if self.num_groups > 0:
            self.group_size = rheader["ncpu"] // self.num_groups

        # Read namelist.txt file (if any)
        self.read_namelist()