    def drop_duplicates(self, subset=None, keep="first", inplace=False):
        """Return DataFrame with duplicate rows removed, optionally only considering certain columns

            Args:
                subset : column label or sequence of labels, optional
                    Only consider certain columns for identifying duplicates, by
                    default use all of the columns
                keep : {'first', 'last', False}, default 'first'
                    - ``first`` : Drop duplicates except for the first occurrence.
                    - ``last`` : Drop duplicates except for the last occurrence.
                    - False : Drop all duplicates.
                inplace : boolean, default False
                    Whether to drop duplicates in place or to return a copy

            Returns:
                deduplicated : DataFrame
        """
        inplace = validate_bool_kwarg(inplace, "inplace")
        duplicates = self.duplicated(subset=subset, keep=keep)
        indices, = duplicates.values.nonzero()
        return self.drop(index=self.index[indices], inplace=inplace)