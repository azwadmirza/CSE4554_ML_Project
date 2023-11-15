    def __delitem__(self, key):
        """Delete a column by key. `del a[key]` for example.
           Operation happens in place.

           Notes: This operation happen on row and column partition
                  simultaneously. No rebuild.
        Args:
            key: key to delete
        """
        # Create helper method for deleting column(s) in row partition.
        def del_helper(df, to_delete):
            cols = df.columns[to_delete]  # either int or an array of ints

            if not is_list_like(cols):
                cols = [cols]

            for col in cols:
                df.__delitem__(col)

            # Reset the column index to conserve space
            df.columns = pd.RangeIndex(0, len(df.columns))
            return df

        # This structure is used to get the correct index inside the partition.
        del_df = self._col_metadata[key]

        # We need to standardize between multiple and single occurrences in the
        # columns. Putting single occurrences in a pd.DataFrame and transposing
        # results in the same structure as multiple with 'loc'.
        if isinstance(del_df, pd.Series):
            del_df = pd.DataFrame(del_df).T

        # Cast cols as pd.Series as duplicate columns mean result may be
        # np.int64 or pd.Series
        col_parts_to_del = \
            pd.Series(del_df['partition'].copy()).unique()
        self._col_metadata.drop(key)

        for i in col_parts_to_del:
            # Compute the correct index inside the partition to delete.
            to_delete_in_partition = \
                del_df[del_df['partition'] == i]['index_within_partition']

            for j in range(self._block_partitions.shape[0]):
                self._block_partitions[j, i] = _deploy_func.remote(
                    del_helper, self._block_partitions[j, i],
                    to_delete_in_partition)

        self._col_metadata.reset_partition_coords(col_parts_to_del)