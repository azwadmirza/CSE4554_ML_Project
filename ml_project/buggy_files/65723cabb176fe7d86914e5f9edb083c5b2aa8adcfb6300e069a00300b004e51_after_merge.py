    def _compute_efficient(self, bw):
        """
        Computes the bandwidth by estimating the scaling factor (c)
        in n_res resamples of size ``n_sub`` (in `randomize` case), or by
        dividing ``nobs`` into as many ``n_sub`` blocks as needed (if
        `randomize` is False).

        References
        ----------
        See p.9 in socserv.mcmaster.ca/racine/np_faq.pdf
        """
        nobs = self.nobs
        n_sub = self.n_sub
        data = copy.deepcopy(self.data)
        n_cvars = self.data_type.count('c')
        co = 4  # 2*order of continuous kernel
        do = 4  # 2*order of discrete kernel
        _, ix_ord, ix_unord = _get_type_pos(self.data_type)

        # Define bounds for slicing the data
        if self.randomize:
            # randomize chooses blocks of size n_sub, independent of nobs
            bounds = [None] * self.n_res
        else:
            bounds = [(i * n_sub, (i+1) * n_sub) for i in range(nobs // n_sub)]
            if nobs % n_sub > 0:
                bounds.append((nobs - nobs % n_sub, nobs))

        n_blocks = self.n_res if self.randomize else len(bounds)
        sample_scale = np.empty((n_blocks, self.k_vars))
        only_bw = np.empty((n_blocks, self.k_vars))

        class_type, class_vars = self._get_class_vars_type()
        if has_joblib:
            # `res` is a list of tuples (sample_scale_sub, bw_sub)
            res = joblib.Parallel(n_jobs=self.n_jobs) \
                (joblib.delayed(_compute_subset) \
                (class_type, data, bw, co, do, n_cvars, ix_ord, ix_unord, \
                n_sub, class_vars, self.randomize, bounds[i]) \
                for i in range(n_blocks))
        else:
            res = []
            for i in xrange(n_blocks):
                res.append(_compute_subset(class_type, data, bw, co, do,
                                           n_cvars, ix_ord, ix_unord, n_sub,
                                           class_vars, self.randomize,
                                           bounds[i]))

        for i in xrange(n_blocks):
            sample_scale[i, :] = res[i][0]
            only_bw[i, :] = res[i][1]

        s = self._compute_dispersion(data)
        order_func = np.median if self.return_median else np.mean
        m_scale = order_func(sample_scale, axis=0)
        # TODO: Check if 1/5 is correct in line below!
        bw = m_scale * s * nobs**(-1. / (n_cvars + co))
        bw[ix_ord] = m_scale[ix_ord] * nobs**(-2./ (n_cvars + do))
        bw[ix_unord] = m_scale[ix_unord] * nobs**(-2./ (n_cvars + do))

        if self.return_only_bw:
            bw = np.median(only_bw, axis=0)

        return bw