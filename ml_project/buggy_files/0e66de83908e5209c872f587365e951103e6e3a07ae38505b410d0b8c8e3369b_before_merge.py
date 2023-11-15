    def reset_index(self, level=None, drop=False, inplace=False, col_level=0,
                    col_fill=''):
        """
        For DataFrame with multi-level index, return new DataFrame with
        labeling information in the columns under the index names, defaulting
        to 'level_0', 'level_1', etc. if any are None. For a standard index,
        the index name will be used (if set), otherwise a default 'index' or
        'level_0' (if 'index' is already taken) will be used.

        Parameters
        ----------
        level : int, str, tuple, or list, default None
            Only remove the given levels from the index. Removes all levels by
            default
        drop : boolean, default False
            Do not try to insert index into dataframe columns. This resets
            the index to the default integer index.
        inplace : boolean, default False
            Modify the DataFrame in place (do not create a new object)
        col_level : int or str, default 0
            If the columns have multiple levels, determines which level the
            labels are inserted into. By default it is inserted into the first
            level.
        col_fill : object, default ''
            If the columns have multiple levels, determines how the other
            levels are named. If None then the index name is repeated.

        Returns
        -------
        resetted : DataFrame
        """
        inplace = validate_bool_kwarg(inplace, 'inplace')
        if inplace:
            new_obj = self
        else:
            new_obj = self.copy()

        def _maybe_casted_values(index, labels=None):
            if isinstance(index, PeriodIndex):
                values = index.asobject.values
            elif isinstance(index, DatetimeIndex) and index.tz is not None:
                values = index
            else:
                values = index.values
                if values.dtype == np.object_:
                    values = lib.maybe_convert_objects(values)

            # if we have the labels, extract the values with a mask
            if labels is not None:
                mask = labels == -1

                # we can have situations where the whole mask is -1,
                # meaning there is nothing found in labels, so make all nan's
                if mask.all():
                    values = np.empty(len(mask))
                    values.fill(np.nan)
                else:
                    values = values.take(labels)
                    if mask.any():
                        values, changed = maybe_upcast_putmask(
                            values, mask, np.nan)
            return values

        new_index = _default_index(len(new_obj))
        if isinstance(self.index, MultiIndex):
            if level is not None:
                if not isinstance(level, (tuple, list)):
                    level = [level]
                level = [self.index._get_level_number(lev) for lev in level]
                if len(level) < len(self.index.levels):
                    new_index = self.index.droplevel(level)

            if not drop:
                names = self.index.names
                zipped = lzip(self.index.levels, self.index.labels)

                multi_col = isinstance(self.columns, MultiIndex)
                for i, (lev, lab) in reversed(list(enumerate(zipped))):
                    col_name = names[i]
                    if col_name is None:
                        col_name = 'level_%d' % i

                    if multi_col:
                        if col_fill is None:
                            col_name = tuple([col_name] * self.columns.nlevels)
                        else:
                            name_lst = [col_fill] * self.columns.nlevels
                            lev_num = self.columns._get_level_number(col_level)
                            name_lst[lev_num] = col_name
                            col_name = tuple(name_lst)

                    # to ndarray and maybe infer different dtype
                    level_values = _maybe_casted_values(lev, lab)
                    if level is None or i in level:
                        new_obj.insert(0, col_name, level_values)

        elif not drop:
            name = self.index.name
            if name is None or name == 'index':
                name = 'index' if 'index' not in self else 'level_0'
            if isinstance(self.columns, MultiIndex):
                if col_fill is None:
                    name = tuple([name] * self.columns.nlevels)
                else:
                    name_lst = [col_fill] * self.columns.nlevels
                    lev_num = self.columns._get_level_number(col_level)
                    name_lst[lev_num] = name
                    name = tuple(name_lst)
            values = _maybe_casted_values(self.index)
            new_obj.insert(0, name, values)

        new_obj.index = new_index
        if not inplace:
            return new_obj