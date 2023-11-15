    def merge(self, right, **kwargs):
        """
        Merge DataFrame or named Series objects with a database-style join.

        Parameters
        ----------
        right : PandasQueryCompiler
            The query compiler of the right DataFrame to merge with.

        Returns
        -------
        PandasQueryCompiler
            A new query compiler that contains result of the merge.

        Notes
        -----
        See pd.merge or pd.DataFrame.merge for more info on kwargs.
        """
        how = kwargs.get("how", "inner")
        on = kwargs.get("on", None)
        left_on = kwargs.get("left_on", None)
        right_on = kwargs.get("right_on", None)
        left_index = kwargs.get("left_index", False)
        right_index = kwargs.get("right_index", False)
        sort = kwargs.get("sort", False)

        if how in ["left", "inner"] and left_index is False and right_index is False:
            right = right.to_pandas()

            kwargs["sort"] = False

            def map_func(left, right=right, kwargs=kwargs):
                return pandas.merge(left, right, **kwargs)

            new_self = self.__constructor__(
                self._modin_frame._apply_full_axis(1, map_func)
            )
            is_reset_index = True
            if left_on and right_on:
                left_on = left_on if is_list_like(left_on) else [left_on]
                right_on = right_on if is_list_like(right_on) else [right_on]
                is_reset_index = (
                    False
                    if any(o in new_self.index.names for o in left_on)
                    and any(o in right.index.names for o in right_on)
                    else True
                )
                if sort:
                    new_self = (
                        new_self.sort_rows_by_column_values(left_on.append(right_on))
                        if is_reset_index
                        else new_self.sort_index(axis=0, level=left_on.append(right_on))
                    )
            if on:
                on = on if is_list_like(on) else [on]
                is_reset_index = not any(
                    o in new_self.index.names and o in right.index.names for o in on
                )
                if sort:
                    new_self = (
                        new_self.sort_rows_by_column_values(on)
                        if is_reset_index
                        else new_self.sort_index(axis=0, level=on)
                    )
            return new_self.reset_index(drop=True) if is_reset_index else new_self
        else:
            return self.default_to_pandas(pandas.DataFrame.merge, right, **kwargs)