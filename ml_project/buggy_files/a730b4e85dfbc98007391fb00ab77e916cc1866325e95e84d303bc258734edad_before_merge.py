    def _translate(self):
        """Classify the netCDF variables into CF-netCDF variables."""

        netcdf_variable_names = self._dataset.variables.keys()

        # Identify all CF coordinate variables first. This must be done
        # first as, by CF convention, the definition of a CF auxiliary
        # coordinate variable may include a scalar CF coordinate variable,
        # whereas we want these two types of variables to be mutually exclusive.
        coords = CFCoordinateVariable.identify(self._dataset.variables,
                                               monotonic=self._check_monotonic)
        self.cf_group.update(coords)
        coordinate_names = self.cf_group.coordinates.keys()

        # Identify all CF variables EXCEPT for the "special cases".
        for variable_type in self._variable_types:
            # Prevent grid mapping variables being mis-identified as CF coordinate variables.
            ignore = None if issubclass(variable_type, CFGridMappingVariable) else coordinate_names
            self.cf_group.update(variable_type.identify(self._dataset.variables, ignore=ignore))

        # Identify global netCDF attributes.
        attr_dict = {attr_name: getattr(self._dataset, attr_name, '') for
                        attr_name in self._dataset.ncattrs()}
        self.cf_group.global_attributes.update(attr_dict)

        # Identify and register all CF formula terms.
        formula_terms = _CFFormulaTermsVariable.identify(self._dataset.variables)

        for cf_var in formula_terms.itervalues():
            for cf_root, cf_term in cf_var.cf_terms_by_root.iteritems():
                # Ignore formula terms owned by a bounds variable.
                if cf_root not in self.cf_group.bounds:
                    cf_name = cf_var.cf_name
                    if cf_var.cf_name not in self.cf_group:
                        self.cf_group[cf_name] = CFAuxiliaryCoordinateVariable(cf_name, cf_var.cf_data)
                    self.cf_group[cf_name].add_formula_term(cf_root, cf_term)

        # Determine the CF data variables.
        data_variable_names = set(netcdf_variable_names) - set(self.cf_group.ancillary_variables) - \
                              set(self.cf_group.auxiliary_coordinates) - set(self.cf_group.bounds) - \
                              set(self.cf_group.climatology) - set(self.cf_group.coordinates) - \
                              set(self.cf_group.grid_mappings) - set(self.cf_group.labels) - \
                              set(self.cf_group.cell_measures)

        for name in data_variable_names:
            self.cf_group[name] = CFDataVariable(name, self._dataset.variables[name])