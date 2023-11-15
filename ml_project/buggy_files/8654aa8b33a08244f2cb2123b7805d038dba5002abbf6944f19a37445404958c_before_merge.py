        def compute_pointer(self, context, builder, indices, arrty, arr):
            assert len(indices) == self.ndim
            return cgutils.get_item_pointer(builder, arrty, arr,
                                            indices, wraparound=False)