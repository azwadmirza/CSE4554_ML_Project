    def scale_swath_data(self, data, scaling_factors):
        """Scale swath data using scaling factors and offsets.

        Multi-granule (a.k.a. aggregated) files will have more than the usual two values.
        """
        num_grans = len(scaling_factors) // 2
        gran_size = data.shape[0] // num_grans
        factors = scaling_factors.where(scaling_factors > -999)
        factors = xr.DataArray(np.repeat(factors.values[None, :], gran_size, axis=0),
                               dims=(data.dims[0], 'factors'))
        data = data * factors[:, 0] + factors[:, 1]
        return data