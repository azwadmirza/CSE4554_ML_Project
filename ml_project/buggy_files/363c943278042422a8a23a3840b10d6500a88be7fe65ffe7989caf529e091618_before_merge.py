    def impute_pmm(self, vname):
        """
        Use predictive mean matching to impute missing values.

        Notes
        -----
        The `perturb_params` method must be called first to define the
        model.
        """

        k_pmm = self.k_pmm

        endog_obs, exog_obs, exog_miss, predict_obs_kwds, predict_miss_kwds =\
                   self.get_split_data(vname)

        # Predict imputed variable for both missing and non-missing
        # observations
        model = self.models[vname]
        pendog_obs = model.predict(self.params[vname], exog_obs, **predict_obs_kwds)
        pendog_miss = model.predict(self.params[vname], exog_miss, **predict_miss_kwds)

        pendog_obs = self._get_predicted(pendog_obs)
        pendog_miss = self._get_predicted(pendog_miss)

        # Jointly sort the observed and predicted endog values for the
        # cases with observed values.
        ii = np.argsort(pendog_obs)
        endog_obs = endog_obs[ii]
        pendog_obs = pendog_obs[ii]

        # Find the closest match to the predicted endog values for
        # cases with missing endog values.
        ix = np.searchsorted(pendog_obs, pendog_miss)

        # Get the indices for the closest k_pmm values on
        # either side of the closest index.
        ixm = ix[:, None] +  np.arange(-k_pmm, k_pmm)[None, :]

        # Account for boundary effects
        msk = np.nonzero((ixm < 0) | (ixm > len(endog_obs) - 1))
        ixm = np.clip(ixm, 0, len(endog_obs) - 1)

        # Get the distances
        dx = pendog_miss[:, None] - pendog_obs[ixm]
        dx = np.abs(dx)
        dx[msk] = np.inf

        # Closest positions in ix, row-wise.
        dxi = np.argsort(dx, 1)[:, 0:k_pmm]

        # Choose a column for each row.
        ir = np.random.randint(0, k_pmm, len(pendog_miss))

        # Unwind the indices
        jj = np.arange(dxi.shape[0])
        ix = dxi[[jj, ir]]
        iz = ixm[[jj, ix]]

        imputed_miss = np.array(endog_obs[iz])
        self._store_changes(vname, imputed_miss)