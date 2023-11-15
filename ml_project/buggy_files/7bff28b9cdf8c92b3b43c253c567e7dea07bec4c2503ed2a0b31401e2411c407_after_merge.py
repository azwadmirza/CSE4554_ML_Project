    def copy(self, column_names=None, virtual=True):
        df = DataFrameArrays()
        df._length_unfiltered = self._length_unfiltered
        df._length_original = self._length_original
        df._cached_filtered_length = self._cached_filtered_length
        df._index_end = self._index_end
        df._index_start = self._index_start
        df._active_fraction = self._active_fraction
        df._renamed_columns = list(self._renamed_columns)
        df._column_aliases = dict(self._column_aliases)
        df.units.update(self.units)
        df.variables.update(self.variables)  # we add all, could maybe only copy used
        df._categories.update(self._categories)
        if column_names is None:
            column_names = self.get_column_names(hidden=True, alias=False)
        all_column_names = self.get_column_names(hidden=True, alias=False)

        # put in the selections (thus filters) in place
        # so drop moves instead of really dropping it
        df.functions.update(self.functions)
        for key, value in self.selection_histories.items():
            # TODO: selection_histories begin a defaultdict always gives
            # us the filtered selection, so check if we really have a
            # selection
            if self.get_selection(key):
                df.selection_histories[key] = list(value)
                # the filter should never be modified, so we can share a reference
                # except when we add filter on filter using
                # df = df[df.x>0]
                # df = df[df.x < 10]
                # in that case we make a copy in __getitem__
                if key == FILTER_SELECTION_NAME:
                    df._selection_masks[key] = self._selection_masks[key]
                else:
                    df._selection_masks[key] = vaex.superutils.Mask(df._length_original)
                # and make sure the mask is consistent with the cache chunks
                np.asarray(df._selection_masks[key])[:] = np.asarray(self._selection_masks[key])
        for key, value in self.selection_history_indices.items():
            if self.get_selection(key):
                df.selection_history_indices[key] = value
                # we can also copy the caches, which prevents recomputations of selections
                df._selection_mask_caches[key] = collections.defaultdict(dict)
                df._selection_mask_caches[key].update(self._selection_mask_caches[key])

        if 1:
            # print("-----", column_names)
            depending = set()
            added = set()
            for name in column_names:
                # print("add", name)
                added.add(name)
                if name in self.columns:
                    column = self.columns[name]
                    df.add_column(name, column, dtype=self._dtypes_override.get(name))
                    if isinstance(column, ColumnSparse):
                        df._sparse_matrices[name] = self._sparse_matrices[name]
                elif name in self.virtual_columns:
                    if virtual:  # TODO: check if the ast is cached
                        df.add_virtual_column(name, self.virtual_columns[name])
                        deps = [key for key, value in df._virtual_expressions[name].ast_names.items()]
                        # print("add virtual", name, df._virtual_expressions[name].expression, deps)
                        depending.update(deps)
                else:
                    # this might be an expression, create a valid name
                    self.validate_expression(name)
                    expression = name
                    name = vaex.utils.find_valid_name(name)
                    # add the expression
                    df[name] = df._expr(expression)
                    # then get the dependencies
                    deps = [key for key, value in df._virtual_expressions[name].ast_names.items()]
                    depending.update(deps)
                # print(depending, "after add")
            # depending |= column_names
            # print(depending)
            # print(depending, "before filter")
            if self.filtered:
                selection = self.get_selection(FILTER_SELECTION_NAME)
                depending |= selection._depending_columns(self)
            depending.difference_update(added)  # remove already added
            # print(depending, "after filter")
            # return depending_columns

            hide = []

            while depending:
                new_depending = set()
                for name in depending:
                    added.add(name)
                    if name in self.columns:
                        # print("add column", name)
                        df.add_column(name, self.columns[name], dtype=self._dtypes_override.get(name))
                        # print("and hide it")
                        # df._hide_column(name)
                        hide.append(name)
                    elif name in self.virtual_columns:
                        if virtual:  # TODO: check if the ast is cached
                            df.add_virtual_column(name, self.virtual_columns[name])
                            deps = [key for key, value in self._virtual_expressions[name].ast_names.items()]
                            new_depending.update(deps)
                        # df._hide_column(name)
                        hide.append(name)
                    elif name in self.variables:
                        # if must be a variables?
                        # TODO: what if the variable depends on other variables
                        # we already add all variables
                        # df.add_variable(name, self.variables[name])
                        pass

                # print("new_depending", new_depending)
                new_depending.difference_update(added)
                depending = new_depending
            for name in hide:
                df._hide_column(name)

        else:
            # we copy all columns, but drop the ones that are not wanted
            # this makes sure that needed columns are hidden instead
            def add_columns(columns):
                for name in columns:
                    if name in self.columns:
                        df.add_column(name, self.columns[name], dtype=self._dtypes_override.get(name))
                    elif name in self.virtual_columns:
                        if virtual:
                            df.add_virtual_column(name, self.virtual_columns[name])
                    else:
                        # this might be an expression, create a valid name
                        expression = name
                        name = vaex.utils.find_valid_name(name)
                        df[name] = df._expr(expression)
            # to preserve the order, we first add the ones we want, then the rest
            add_columns(column_names)
            # then the rest
            rest = set(all_column_names) - set(column_names)
            add_columns(rest)
            # and remove them
            for name in rest:
                # if the column should not have been added, drop it. This checks if columns need
                # to be hidden instead, and expressions be rewritten.
                if name not in column_names:
                    df.drop(name, inplace=True)
                    assert name not in df.get_column_names(hidden=True)

        df.copy_metadata(self)
        return df