    def _cdf(self, x, alpha, beta):

        x = np.asarray(x).reshape(1, -1)[0,:]

        x, alpha, beta = np.broadcast_arrays(x, alpha, beta)

        data_in = np.dstack((x, alpha, beta))[0]
        data_out = np.empty(shape=(len(data_in),1))

        fft_min_points_threshold = getattr(self, 'pdf_fft_min_points_threshold', None)
        fft_grid_spacing = getattr(self, 'pdf_fft_grid_spacing', 0.001)
        fft_n_points_two_power = getattr(self, 'pdf_fft_n_points_two_power', None)

        # group data in unique arrays of alpha, beta pairs
        uniq_param_pairs = np.vstack({tuple(row) for row in data_in[:,1:]})
        for pair in uniq_param_pairs:
            data_mask = np.all(data_in[:,1:] == pair, axis=-1)
            data_subset = data_in[data_mask]
            if fft_min_points_threshold is None or len(data_subset) < fft_min_points_threshold:
                data_out[data_mask] = np.array([levy_stable._cdf_single_value_zolotarev(_x, _alpha, _beta)
                            for _x, _alpha, _beta in data_subset]).reshape(len(data_subset), 1)
            else:
                warnings.warn('FFT method is considered experimental for ' +
                              'cumulative distribution function ' +
                              'evaluations. Use Zolotarev’s method instead).',
                              RuntimeWarning)
                _alpha, _beta = pair
                _x = data_subset[:,(0,)]

                # need enough points to "cover" _x for interpolation
                h = fft_grid_spacing
                q = 16 if fft_n_points_two_power is None else int(fft_n_points_two_power)

                density_x, density = levy_stable_gen._pdf_from_cf_with_fft(lambda t: levy_stable_gen._cf(t, _alpha, _beta), h=h, q=q)
                f = interpolate.InterpolatedUnivariateSpline(density_x, np.real(density))
                data_out[data_mask] = np.array([f.integral(self.a, x_1) for x_1 in _x]).reshape(data_out[data_mask].shape)

        return data_out.T[0]