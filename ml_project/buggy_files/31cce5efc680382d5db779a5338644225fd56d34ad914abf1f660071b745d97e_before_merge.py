    def _get_partitions(self):
        if (
            not self._filtered_empties
            and self._lengths_cache is not None
            and self._widths_cache is not None
        ):
            self._partitions_cache = np.array(
                [
                    row
                    for row in [
                        [
                            self._partitions_cache[i][j]
                            for j in range(len(self._partitions_cache[i]))
                            if self.block_lengths[i] != 0 and self.block_widths[j] != 0
                        ]
                        for i in range(len(self._partitions_cache))
                    ]
                    if len(row)
                ]
            )
            self._remove_empty_blocks()
            self._filtered_empties = True
        return self._partitions_cache