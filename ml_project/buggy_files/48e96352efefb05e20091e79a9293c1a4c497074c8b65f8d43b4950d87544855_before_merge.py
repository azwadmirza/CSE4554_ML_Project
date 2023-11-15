    def to_frame(self, index: bool = True, name=None):
        """
        Create a DataFrame with a column containing the Index.

        Parameters
        ----------
        index : bool, default True
            Set the index of the returned DataFrame as the original Index.

        name : object, default None
            The passed name should substitute for the index name (if it has
            one).

        Returns
        -------
        DataFrame
            DataFrame containing the original Index data.

        See Also
        --------
        Index.to_series : Convert an Index to a Series.
        Series.to_frame : Convert Series to DataFrame.

        Examples
        --------
        >>> import mars.dataframe as md
        >>> idx = md.Index(['Ant', 'Bear', 'Cow'], name='animal')
        >>> idx.to_frame().execute()
               animal
        animal
        Ant       Ant
        Bear     Bear
        Cow       Cow

        By default, the original Index is reused. To enforce a new Index:

        >>> idx.to_frame(index=False).execute()
          animal
        0    Ant
        1   Bear
        2    Cow

        To override the name of the resulting column, specify `name`:

        >>> idx.to_frame(index=False, name='zoo').execute()
            zoo
        0   Ant
        1  Bear
        2   Cow
        """
        from . import dataframe_from_tensor

        if isinstance(self.index_value.value, IndexValue.MultiIndex):
            old_names = self.index_value.value.names

            if name is not None and not isinstance(name, Iterable) or isinstance(name, str):
                raise TypeError("'name' must be a list / sequence of column names.")

            name = list(name if name is not None else old_names)
            if len(name) != len(old_names):
                raise ValueError("'name' should have same length as number of levels on index.")

            columns = [old or new or idx for idx, (old, new) in enumerate(zip(old_names, name))]
        else:
            columns = [name or self.name or 0]
        index_ = self if index else None
        return dataframe_from_tensor(self._to_mars_tensor(self, extract_multi_index=True),
                                     index=index_, columns=columns)