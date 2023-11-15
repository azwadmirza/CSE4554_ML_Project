    def compute(self, data, fill_value=None, **kwargs):
        """Resample the given data using bilinear interpolation"""
        del kwargs

        target_shape = self.target_geo_def.shape
        if data.ndim == 3:
            output_shape = list(target_shape)
            output_shape.append(data.shape[-1])
            res = np.zeros(output_shape, dtype=data.dtype)
            for i in range(data.shape[-1]):
                res[:, :, i] = \
                    get_sample_from_bil_info(data[:, :, i].ravel(),
                                             self.cache['bilinear_t'],
                                             self.cache['bilinear_s'],
                                             self.cache['input_idxs'],
                                             self.cache['idx_arr'],
                                             output_shape=target_shape)

        else:
            res = \
                get_sample_from_bil_info(data.ravel(),
                                         self.cache['bilinear_t'],
                                         self.cache['bilinear_s'],
                                         self.cache['input_idxs'],
                                         self.cache['idx_arr'],
                                         output_shape=target_shape)
        res = np.ma.masked_invalid(res)

        return res