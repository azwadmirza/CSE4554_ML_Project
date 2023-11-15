    def _parse_enzo2_parameter_file(self, f):
        for line in (l.strip() for l in f):
            if len(line) < 2: continue
            param, vals = (i.strip() for i in line.split("=",1))
            # First we try to decipher what type of value it is.
            vals = vals.split()
            # Special case approaching.
            if "(do" in vals: vals = vals[:1]
            if len(vals) == 0:
                pcast = str # Assume NULL output
            else:
                v = vals[0]
                # Figure out if it's castable to floating point:
                try:
                    float(v)
                except ValueError:
                    pcast = str
                else:
                    if any("." in v or "e+" in v or "e-" in v for v in vals):
                        pcast = float
                    elif v == "inf":
                        pcast = str
                    else:
                        pcast = int
            # Now we figure out what to do with it.
            if len(vals) == 0:
                vals = ""
            elif len(vals) == 1:
                vals = pcast(vals[0])
            else:
                vals = np.array([pcast(i) for i in vals if i != "-99999"])
            if param.startswith("Append"):
                if param not in self.parameters:
                    self.parameters[param] = []
                self.parameters[param].append(vals)
            else:
                self.parameters[param] = vals
        self.refine_by = self.parameters["RefineBy"]
        self.periodicity = ensure_tuple(
            self.parameters["LeftFaceBoundaryCondition"] == 3)
        self.dimensionality = self.parameters["TopGridRank"]
        if "MetaDataDatasetUUID" in self.parameters:
            self.unique_identifier = self.parameters["MetaDataDatasetUUID"]
        elif "CurrentTimeIdentifier" in self.parameters:
            self.unique_identifier = self.parameters["CurrentTimeIdentifier"]
        else:
            self.unique_identifier = \
                str(int(os.stat(self.parameter_filename)[stat.ST_CTIME]))
        if self.dimensionality > 1:
            self.domain_dimensions = self.parameters["TopGridDimensions"]
            if len(self.domain_dimensions) < 3:
                tmp = self.domain_dimensions.tolist()
                tmp.append(1)
                self.domain_dimensions = np.array(tmp)
                self.periodicity += (False,)
            self.domain_left_edge = np.array(self.parameters["DomainLeftEdge"],
                                             "float64").copy()
            self.domain_right_edge = np.array(self.parameters["DomainRightEdge"],
                                             "float64").copy()
        else:
            self.domain_left_edge = np.array(self.parameters["DomainLeftEdge"],
                                             "float64")
            self.domain_right_edge = np.array(self.parameters["DomainRightEdge"],
                                             "float64")
            self.domain_dimensions = np.array([self.parameters["TopGridDimensions"],1,1])
            self.periodicity += (False, False)

        self.gamma = self.parameters["Gamma"]
        if self.parameters["ComovingCoordinates"]:
            self.cosmological_simulation = 1
            self.current_redshift = self.parameters["CosmologyCurrentRedshift"]
            self.omega_lambda = self.parameters["CosmologyOmegaLambdaNow"]
            self.omega_matter = self.parameters["CosmologyOmegaMatterNow"]
            self.hubble_constant = self.parameters["CosmologyHubbleConstantNow"]
        else:
            self.current_redshift = self.omega_lambda = self.omega_matter = \
                self.hubble_constant = self.cosmological_simulation = 0.0
        self.particle_types = []
        self.current_time = self.parameters["InitialTime"]
        if self.parameters["NumberOfParticles"] > 0 and \
            "AppendActiveParticleType" in self.parameters.keys():
            # If this is the case, then we know we should have a DarkMatter
            # particle type, and we don't need the "io" type.
            self.parameters["AppendActiveParticleType"].append("DarkMatter")
        else:
            # We do not have an "io" type for Enzo particles if the
            # ActiveParticle machinery is on, as we simply will ignore any of
            # the non-DarkMatter particles in that case.  However, for older
            # datasets, we call this particle type "io".
            self.particle_types = ["io"]
        for ptype in self.parameters.get("AppendActiveParticleType", []):
            self.particle_types.append(ptype)
        self.particle_types = tuple(self.particle_types)
        self.particle_types_raw = self.particle_types

        if self.dimensionality == 1:
            self._setup_1d()
        elif self.dimensionality == 2:
            self._setup_2d()