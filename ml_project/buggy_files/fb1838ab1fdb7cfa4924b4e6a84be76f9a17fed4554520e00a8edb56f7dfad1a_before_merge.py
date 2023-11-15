    def reset_partition_coords(self, partitions=None):
        partitions = np.array(partitions)

        for partition in partitions:
            partition_mask = (self._coord_df['partition'] == partition)
            # Since we are replacing columns with RangeIndex inside the
            # partition, we have to make sure that our reference to it is
            # updated as well.
            try:
                self._coord_df.loc[partition_mask,
                                   'index_within_partition'] = [
                    p for p in range(sum(partition_mask))]
            except ValueError:
                # Copy the arrow sealed dataframe so we can mutate it.
                # We only do this the first time we try to mutate the sealed.
                self._coord_df = self._coord_df.copy()
                self._coord_df.loc[partition_mask,
                                   'index_within_partition'] = [
                    p for p in range(sum(partition_mask))]