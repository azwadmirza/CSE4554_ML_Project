    def drop(self, labels, errors='raise'):
        """Drop the specified labels from the IndexMetadata

        Args:
            labels (scalar or list-like):
                The labels to drop
            errors ('raise' or 'ignore'):
                If 'ignore', suppress errors for when labels don't exist

        Returns:
            DataFrame with coordinates of dropped labels
        """
        dropped = self.coords_of(labels)

        # Update first lengths to prevent possible length inconsistencies
        if isinstance(dropped, pd.DataFrame):
            drop_per_part = dropped.groupby(["partition"]).size()\
                    .reindex(index=pd.RangeIndex(len(self._lengths)),
                             fill_value=0)
        elif isinstance(dropped, pd.Series):
            drop_per_part = np.zeros_like(self._lengths)
            drop_per_part[dropped["partition"]] = 1
        else:
            raise AssertionError("Unrecognized result from `coords_of`")
        self._lengths = self._lengths - drop_per_part

        self._coord_df = self._coord_df.drop(labels, errors=errors)
        return dropped