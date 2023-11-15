    def __init__(self, endog, exog, groups, time=None, family=None,
                 cov_struct=None, missing='none', offset=None,
                 dep_data=None, constraint=None, update_dep=True):

        self.missing = missing
        self.dep_data = dep_data
        self.constraint = constraint
        self.update_dep = update_dep

        groups = np.array(groups) # in case groups is pandas
        # Pass groups, time, offset, and dep_data so they are
        # processed for missing data along with endog and exog.
        # Calling super creates self.exog, self.endog, etc. as
        # ndarrays and the original exog, endog, etc. are
        # self.data.endog, etc.
        super(GEE, self).__init__(endog, exog, groups=groups,
                                  time=time, offset=offset,
                                  dep_data=dep_data, missing=missing)

        self._init_keys.extend(["update_dep", "constraint", "family",
                                "cov_struct"])

        # Handle the family argument
        if family is None:
            family = families.Gaussian()
        else:
            if not issubclass(family.__class__, families.Family):
                raise ValueError("GEE: `family` must be a genmod "
                                 "family instance")
        self.family = family

        # Handle the cov_struct argument
        if cov_struct is None:
            cov_struct = dependence_structures.Independence()
        else:
            if not issubclass(cov_struct.__class__, CovStruct):
                raise ValueError("GEE: `cov_struct` must be a genmod "
                                 "cov_struct instance")

        self.cov_struct = cov_struct

        if offset is None:
            self.offset = np.zeros(self.exog.shape[0],
                                   dtype=np.float64)
        else:
            self.offset = offset

        # Handle the constraint
        self.constraint = None
        if constraint is not None:
            if len(constraint) != 2:
                raise ValueError("GEE: `constraint` must be a 2-tuple.")
            if constraint[0].shape[1] != self.exog.shape[1]:
                raise ValueError("GEE: the left hand side of the "
                   "constraint must have the same number of columns "
                   "as the exog matrix.")
            self.constraint = ParameterConstraint(constraint[0],
                                                  constraint[1],
                                                  self.exog)

            self.offset += self.constraint.offset_increment()
            self.exog = self.constraint.reduced_exog()

        # Convert the data to the internal representation, which is a
        # list of arrays, corresponding to the clusters.
        group_labels = sorted(set(groups))
        group_indices = dict((s, []) for s in group_labels)
        for i in range(len(self.endog)):
            group_indices[groups[i]].append(i)
        for k in iterkeys(group_indices):
            group_indices[k] = np.asarray(group_indices[k])
        self.group_indices = group_indices
        self.group_labels = group_labels

        self.endog_li = self.cluster_list(self.endog)
        self.exog_li = self.cluster_list(self.exog)

        self.num_group = len(self.endog_li)

        # Time defaults to a 1d grid with equal spacing
        if self.time is not None:
            self.time = np.asarray(self.time, np.float64)
            if self.time.ndim == 1:
                self.time = self.time[:,None]
            self.time_li = self.cluster_list(self.time)
        else:
            self.time_li = \
                [np.arange(len(y), dtype=np.float64)[:, None]
                 for y in self.endog_li]
            self.time = np.concatenate(self.time_li)

        self.offset_li = self.cluster_list(self.offset)
        if constraint is not None:
            self.constraint.exog_fulltrans_li = \
                self.cluster_list(self.constraint.exog_fulltrans)

        self.family = family

        self.cov_struct.initialize(self)

        # Total sample size
        group_ns = [len(y) for y in self.endog_li]
        self.nobs = sum(group_ns)

        # mean_deriv is the derivative of E[endog|exog] with respect
        # to params
        try:
            # This custom mean_deriv is currently only used for the
            # multinomial logit model
            self.mean_deriv = self.family.link.mean_deriv
        except AttributeError:
            # Otherwise it can be obtained easily from inverse_deriv
            mean_deriv_lpr = self.family.link.inverse_deriv

            def mean_deriv(exog, lpr):
                dmat = exog * mean_deriv_lpr(lpr)[:, None]
                return dmat

            self.mean_deriv = mean_deriv

        # mean_deriv_exog is the derivative of E[endog|exog] with
        # respect to exog
        try:
            # This custom mean_deriv_exog is currently only used for
            # the multinomial logit model
            self.mean_deriv_exog = self.family.link.mean_deriv_exog
        except AttributeError:
            # Otherwise it can be obtained easily from inverse_deriv
            mean_deriv_lpr = self.family.link.inverse_deriv

            def mean_deriv_exog(exog, params):
                lpr = np.dot(exog, params)
                dmat = np.outer(mean_deriv_lpr(lpr), params)
                return dmat

            self.mean_deriv_exog = mean_deriv_exog

        # Skip the covariance updates if all groups have a single
        # observation (reduces to fitting a GLM).
        maxgroup = max([len(x) for x in self.endog_li])
        if maxgroup == 1:
            self.update_dep = False