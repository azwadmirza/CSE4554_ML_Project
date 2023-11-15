    def compute(self, data, fill_value=0, weight_count=10000, weight_min=0.01,
                weight_distance_max=1.0, weight_sum_min=-1.0,
                maximum_weight_mode=False, **kwargs):
        rows = self.cache["rows"]
        cols = self.cache["cols"]

        # if the data is scan based then check its metadata or the passed
        # kwargs otherwise assume the entire input swath is one large
        # "scanline"
        rows_per_scan = getattr(data, "info", kwargs).get(
            "rows_per_scan", data.shape[0])
        if hasattr(data, 'mask'):
            mask = data.mask
            data = data.data
            data[mask] = np.nan

        if data.ndim >= 3:
            data_in = tuple(data[..., i] for i in range(data.shape[-1]))
        else:
            data_in = data

        num_valid_points, res = \
            fornav(cols, rows, self.target_geo_def,
                   data_in,
                   rows_per_scan=rows_per_scan,
                   weight_count=weight_count,
                   weight_min=weight_min,
                   weight_distance_max=weight_distance_max,
                   weight_sum_min=weight_sum_min,
                   maximum_weight_mode=maximum_weight_mode)

        if data.ndim >= 3:
            # convert 'res' from tuple of arrays to one array
            res = np.dstack(res)
            num_valid_points = sum(num_valid_points)

        grid_covered_ratio = num_valid_points / float(res.size)
        grid_covered = grid_covered_ratio > self.grid_coverage
        if not grid_covered:
            msg = "EWA resampling only found %f%% of the grid covered "
            "(need %f%%)" % (grid_covered_ratio * 100,
                             self.grid_coverage * 100)
            raise RuntimeError(msg)
        LOG.debug("EWA resampling found %f%% of the grid covered" %
                  (grid_covered_ratio * 100))

        return np.ma.masked_invalid(res)