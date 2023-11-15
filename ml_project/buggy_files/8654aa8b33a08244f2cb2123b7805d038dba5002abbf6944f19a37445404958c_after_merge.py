        def compute_pointer(self, context, builder, indices, arrty, arr):
            assert len(indices) == self.ndim
            return cgutils.get_item_pointer(context, builder, arrty, arr,
                                            indices, wraparound=False)