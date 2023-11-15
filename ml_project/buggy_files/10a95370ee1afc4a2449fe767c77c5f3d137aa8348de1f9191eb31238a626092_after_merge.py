    def set_units(self):
        """
        Creates the unit registry for this dataset.

        """

        if getattr(self, "cosmological_simulation", False):
            # this dataset is cosmological, so add cosmological units.
            self.unit_registry.modify("h", self.hubble_constant)
            # Comoving lengths
            for my_unit in ["m", "pc", "AU", "au"]:
                new_unit = "%scm" % my_unit
                my_u = Unit(my_unit, registry=self.unit_registry)
                self.unit_registry.add(
                    new_unit,
                    my_u.base_value / (1 + self.current_redshift),
                    dimensions.length,
                    "\\rm{%s}/(1+z)" % my_unit,
                    prefixable=True,
                )
            self.unit_registry.modify("a", 1 / (1 + self.current_redshift))

        self.set_code_units()

        if getattr(self, "cosmological_simulation", False):
            # this dataset is cosmological, add a cosmology object

            # Set dynamical dark energy parameters
            use_dark_factor = getattr(self, "use_dark_factor", False)
            w_0 = getattr(self, "w_0", -1.0)
            w_a = getattr(self, "w_a", 0.0)

            # many frontends do not set this
            setdefaultattr(self, "omega_radiation", 0.0)

            self.cosmology = Cosmology(
                hubble_constant=self.hubble_constant,
                omega_matter=self.omega_matter,
                omega_lambda=self.omega_lambda,
                omega_radiation=self.omega_radiation,
                use_dark_factor=use_dark_factor,
                w_0=w_0,
                w_a=w_a,
            )
            self.critical_density = self.cosmology.critical_density(
                self.current_redshift
            )
            self.scale_factor = 1.0 / (1.0 + self.current_redshift)