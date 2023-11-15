    def get_domain(self, domain, data):
        """Create domain (and dataset) from changes made in the widget.

        Parameters
        ----------
        domain : old domain
        data : source data

        Returns
        -------
        (new_domain, [attribute_columns, class_var_columns, meta_columns])
        """
        variables = self.model().variables
        places = [[], [], []]  # attributes, class_vars, metas
        cols = [[], [], []]  # Xcols, Ycols, Mcols

        def is_missing(x):
            return str(x) in ("nan", "")

        for (name, tpe, place, _, _), (orig_var, orig_plc) in \
                zip(variables,
                        chain([(at, Place.feature) for at in domain.attributes],
                              [(cl, Place.class_var) for cl in domain.class_vars],
                              [(mt, Place.meta) for mt in domain.metas])):
            if place == Place.skip:
                continue
            if orig_plc == Place.meta:
                col_data = data[:, orig_var].metas
            elif orig_plc == Place.class_var:
                col_data = data[:, orig_var].Y
            else:
                col_data = data[:, orig_var].X
            col_data = col_data.ravel()
            if name == orig_var.name and tpe == type(orig_var):
                var = orig_var
            elif tpe == type(orig_var):
                # change the name so that all_vars will get the correct name
                orig_var.name = name
                var = orig_var
            elif tpe == DiscreteVariable:
                values = list(str(i) for i in np.unique(col_data) if not is_missing(i))
                var = tpe(name, values)
                col_data = [np.nan if is_missing(x) else values.index(str(x))
                            for x in col_data]
            elif tpe == StringVariable and type(orig_var) == DiscreteVariable:
                var = tpe(name)
                col_data = [orig_var.repr_val(x) if not np.isnan(x) else ""
                            for x in col_data]
            else:
                var = tpe(name)
            places[place].append(var)
            cols[place].append(col_data)
        domain = Domain(*places)
        return domain, cols