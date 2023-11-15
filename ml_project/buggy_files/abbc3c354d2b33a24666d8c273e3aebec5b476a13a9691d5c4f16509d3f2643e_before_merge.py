    def _create_blocks(self, obj: FrameOrSeriesUnion):
        """
        Split data into blocks & return conformed data.
        """
        # Ensure the object we're rolling over is monotonically sorted relative
        # to the groups
        groupby_order = np.concatenate(
            list(self._groupby.grouper.indices.values())
        ).astype(np.int64)
        obj = obj.take(groupby_order)
        return super()._create_blocks(obj)