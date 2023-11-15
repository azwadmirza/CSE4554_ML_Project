    def __call__(self, a, bins, range, weights):
        if range is not None:
            _check_range(range)
        if isinstance(bins, str):
            # string, 'auto', 'stone', ...
            # shape is unknown
            bin_name = bins
            # if `bins` is a string for an automatic method,
            # this will replace it with the number of bins calculated
            if bin_name not in _hist_bin_selectors:
                raise ValueError(
                    f"{bin_name!r} is not a valid estimator for `bins`")
            if weights is not None:
                raise TypeError("Automated estimation of the number of "
                                "bins is not supported for weighted data")
            if isinstance(range, tuple) and len(range) == 2:
                # if `bins` is a string, e.g. 'auto', 'stone'...,
                # and `range` provided as well,
                # `a` should be trimmed first
                first_edge, last_edge = _get_outer_edges(a, range)
                a = a[(a >= first_edge) & (a <= last_edge)]
            shape = (np.nan,)
        elif mt.ndim(bins) == 0:
            try:
                n_equal_bins = operator.index(bins)
            except TypeError:  # pragma: no cover
                raise TypeError(
                    '`bins` must be an integer, a string, or an array')
            if n_equal_bins < 1:
                raise ValueError('`bins` must be positive, when an integer')
            shape = (bins + 1,)
        elif mt.ndim(bins) == 1:
            if not isinstance(bins, TENSOR_TYPE):
                bins = np.asarray(bins)
                if not is_asc_sorted(bins):
                    raise ValueError(
                        '`bins` must increase monotonically, when an array')
            shape = astensor(bins).shape
        else:
            raise ValueError('`bins` must be 1d, when an array')

        inputs = [a]
        if isinstance(bins, TENSOR_TYPE):
            inputs.append(bins)
        if weights is not None:
            inputs.append(weights)
        if a.size > 0 and \
                (isinstance(bins, str) or mt.ndim(bins) == 0) and not range:
            # for bins that is str or integer,
            # requires min max calculated first
            input_min = self._input_min = a.min()
            inputs.append(input_min)
            input_max = self._input_max = a.max()
            inputs.append(input_max)

        return self.new_tensor(inputs, shape=shape, order=TensorOrder.C_ORDER)