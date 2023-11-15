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
        right = right.to_pandas()

        sort = kwargs.get("sort")
        kwargs["sort"] = not sort if sort else sort

        def map_func(left, right=right, kwargs=kwargs):
            return pandas.merge(left, right, **kwargs)

        new_modin_frame = self._modin_frame._apply_full_axis(1, map_func)
        return self.__constructor__(new_modin_frame)