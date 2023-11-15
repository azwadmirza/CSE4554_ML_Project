    def compute(self, data, weight_funcs=None, fill_value=None,
                with_uncert=False, **kwargs):
        del kwargs
        LOG.debug("Resampling " + str(data.name))
        if fill_value is None:
            fill_value = data.attrs.get('_FillValue')
        res = self.resampler.get_sample_from_neighbour_info(data, fill_value)
        return res