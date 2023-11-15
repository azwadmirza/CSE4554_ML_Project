    def get_new_values(self):
        values = self.values
        # place the values
        length, width = self.full_shape
        stride = values.shape[1]
        result_width = width * stride

        new_values = np.empty((length, result_width), dtype=values.dtype)
        new_mask = np.zeros((length, result_width), dtype=bool)

        if issubclass(values.dtype.type, np.integer):
            new_values = new_values.astype(float)

        new_values.fill(np.nan)

        # is there a simpler / faster way of doing this?
        for i in xrange(values.shape[1]):
            chunk = new_values[:, i * width : (i + 1) * width]
            mask_chunk = new_mask[:, i * width : (i + 1) * width]

            chunk.flat[self.mask] = self.sorted_values[:, i]
            mask_chunk.flat[self.mask] = True

        new_values = new_values.take(self.unique_groups, axis=0)
        return new_values, new_mask