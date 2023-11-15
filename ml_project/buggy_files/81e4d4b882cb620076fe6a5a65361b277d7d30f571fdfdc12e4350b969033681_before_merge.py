    def _create_unit_registry(self, unit_system):
        from yt.units import dimensions as dimensions

        # yt assumes a CGS unit system by default (for back compat reasons).
        # Since unyt is MKS by default we specify the MKS values of the base
        # units in the CGS system. So, for length, 1 cm = .01 m. And so on.
        self.unit_registry = UnitRegistry(unit_system=unit_system)
        self.unit_registry.add("code_length", 0.01, dimensions.length)
        self.unit_registry.add("code_mass", 0.001, dimensions.mass)
        self.unit_registry.add("code_density", 1000.0, dimensions.density)
        self.unit_registry.add(
            "code_specific_energy", 1.0, dimensions.energy / dimensions.mass
        )
        self.unit_registry.add("code_time", 1.0, dimensions.time)
        if unit_system == "mks":
            self.unit_registry.add("code_magnetic", 1.0, dimensions.magnetic_field)
        else:
            self.unit_registry.add(
                "code_magnetic", 0.1 ** 0.5, dimensions.magnetic_field_cgs
            )
        self.unit_registry.add("code_temperature", 1.0, dimensions.temperature)
        self.unit_registry.add("code_pressure", 0.1, dimensions.pressure)
        self.unit_registry.add("code_velocity", 0.01, dimensions.velocity)
        self.unit_registry.add("code_metallicity", 1.0, dimensions.dimensionless)
        self.unit_registry.add("h", 1.0, dimensions.dimensionless, r"h")
        self.unit_registry.add("a", 1.0, dimensions.dimensionless)