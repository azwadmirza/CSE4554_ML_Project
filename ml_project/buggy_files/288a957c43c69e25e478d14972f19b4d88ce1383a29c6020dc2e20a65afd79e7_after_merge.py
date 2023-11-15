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

        for (name, tpe, place, _, _), (orig_var, orig_plc) in \
                zip(variables,
                        chain([(at, Place.feature) for at in domain.attributes],
                              [(cl, Place.class_var) for cl in domain.class_vars],
                              [(mt, Place.meta) for mt in domain.metas])):
            if place == Place.skip:
                continue

            col_data = self._get_column(data, orig_var, orig_plc)
            is_sparse = sp.issparse(col_data)
            if name == orig_var.name and tpe == type(orig_var):
                var = orig_var
            elif tpe == type(orig_var):
                # change the name so that all_vars will get the correct name
                orig_var.name = name
                var = orig_var
            elif tpe == DiscreteVariable:
                values = list(str(i) for i in unique(col_data) if not self._is_missing(i))
                var = tpe(name, values)
                col_data = [np.nan if self._is_missing(x) else values.index(str(x))
                            for x in self._iter_vals(col_data)]
                col_data = self._to_column(col_data, is_sparse)
            elif tpe == StringVariable and type(orig_var) == DiscreteVariable:
                var = tpe(name)
                col_data = [orig_var.repr_val(x) if not np.isnan(x) else ""
                            for x in self._iter_vals(col_data)]
                # don't obey sparsity for StringVariable since they are
                # in metas which are transformed to dense below
                col_data = self._to_column(col_data, False, dtype=object)
            else:
                var = tpe(name)
            places[place].append(var)
            cols[place].append(col_data)

        # merge columns for X, Y and metas
        feats = cols[Place.feature]
        X = self._merge(feats) if len(feats) else np.empty((len(data), 0))
        Y = self._merge(cols[Place.class_var], force_dense=True)
        m = self._merge(cols[Place.meta], force_dense=True)
        domain = Domain(*places)
        return domain, [X, Y, m]