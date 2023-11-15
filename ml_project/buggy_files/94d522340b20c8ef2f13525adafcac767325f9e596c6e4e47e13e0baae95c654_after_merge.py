    def fit(self, X, y):
        """Fit linear model with coordinate descent

        Fit is on grid of alphas and best alpha estimated by cross-validation.

        Parameters
        ----------
        X : {array-like}, shape (n_samples, n_features)
            Training data. Pass directly as float64, Fortran-contiguous data
            to avoid unnecessary memory duplication. If y is mono-output,
            X can be sparse.

        y : array-like, shape (n_samples,) or (n_samples, n_targets)
            Target values
        """
        y = np.asarray(y, dtype=np.float64)

        if hasattr(self, 'l1_ratio'):
            model_str = 'ElasticNet'
        else:
            model_str = 'Lasso'

        if isinstance(self, ElasticNetCV) or isinstance(self, LassoCV):
            if model_str == 'ElasticNet':
                model = ElasticNet()
            else:
                model = Lasso()
            if y.ndim > 1:
                raise ValueError("For multi-task outputs, use "
                                 "MultiTask%sCV" % (model_str))
        else:
            if sparse.isspmatrix(X):
                raise TypeError("X should be dense but a sparse matrix was"
                                "passed")
            elif y.ndim == 1:
                raise ValueError("For mono-task outputs, use "
                                 "%sCV" % (model_str))
            if model_str == 'ElasticNet':
                model = MultiTaskElasticNet()
            else:
                model = MultiTaskLasso()

        # This makes sure that there is no duplication in memory.
        # Dealing right with copy_X is important in the following:
        # Multiple functions touch X and subsamples of X and can induce a
        # lot of duplication of memory
        copy_X = self.copy_X and self.fit_intercept

        if isinstance(X, np.ndarray) or sparse.isspmatrix(X):
            # Keep a reference to X
            reference_to_old_X = X
            # Let us not impose fortran ordering or float64 so far: it is
            # not useful for the cross-validation loop and will be done
            # by the model fitting itself
            X = atleast2d_or_csc(X, copy=False)
            if sparse.isspmatrix(X):
                if not np.may_share_memory(reference_to_old_X.data, X.data):
                    # X is a sparse matrix and has been copied
                    copy_X = False
            elif not np.may_share_memory(reference_to_old_X, X):
                # X has been copied
                copy_X = False
            del reference_to_old_X
        else:
            X = atleast2d_or_csc(X, dtype=np.float64, order='F',
                                 copy=copy_X)
            copy_X = False

        if X.shape[0] != y.shape[0]:
            raise ValueError("X and y have inconsistent dimensions (%d != %d)"
                             % (X.shape[0], y.shape[0]))

        # All LinearModelCV parameters except 'cv' are acceptable
        path_params = self.get_params()
        if 'l1_ratio' in path_params:
            l1_ratios = np.atleast_1d(path_params['l1_ratio'])
            # For the first path, we need to set l1_ratio
            path_params['l1_ratio'] = l1_ratios[0]
        else:
            l1_ratios = [1, ]
        path_params.pop('cv', None)
        path_params.pop('n_jobs', None)

        alphas = self.alphas
        n_l1_ratio = len(l1_ratios)
        if alphas is None:
            alphas = []
            for l1_ratio in l1_ratios:
                alphas.append(_alpha_grid(
                    X, y, l1_ratio=l1_ratio,
                    fit_intercept=self.fit_intercept,
                    eps=self.eps, n_alphas=self.n_alphas,
                    normalize=self.normalize,
                    copy_X=self.copy_X))
        else:
            # Making sure alphas is properly ordered.
            alphas = np.tile(np.sort(alphas)[::-1], (n_l1_ratio, 1))
        # We want n_alphas to be the number of alphas used for each l1_ratio.
        n_alphas = len(alphas[0])
        path_params.update({'n_alphas': n_alphas})

        path_params['copy_X'] = copy_X
        # We are not computing in parallel, we can modify X
        # inplace in the folds
        if not (self.n_jobs == 1 or self.n_jobs is None):
            path_params['copy_X'] = False

        # init cross-validation generator
        cv = check_cv(self.cv, X)

        # Compute path for all folds and compute MSE to get the best alpha
        folds = list(cv)
        best_mse = np.inf

        # We do a double for loop folded in one, in order to be able to
        # iterate in parallel on l1_ratio and folds
        jobs = (delayed(_path_residuals)(X, y, train, test, self.path,
                                         path_params, alphas=this_alphas,
                                         l1_ratio=this_l1_ratio, X_order='F',
                                         dtype=np.float64)
                for this_l1_ratio, this_alphas in zip(l1_ratios, alphas)
                for train, test in folds)
        mse_paths = Parallel(n_jobs=self.n_jobs, verbose=self.verbose,
                             backend="threading")(jobs)
        mse_paths = np.reshape(mse_paths, (n_l1_ratio, len(folds), -1))
        mean_mse = np.mean(mse_paths, axis=1)
        self.mse_path_ = np.squeeze(np.rollaxis(mse_paths, 2, 1))
        for l1_ratio, l1_alphas, mse_alphas in zip(l1_ratios, alphas,
                                                   mean_mse):
            i_best_alpha = np.argmin(mse_alphas)
            this_best_mse = mse_alphas[i_best_alpha]
            if this_best_mse < best_mse:
                best_alpha = l1_alphas[i_best_alpha]
                best_l1_ratio = l1_ratio
                best_mse = this_best_mse

        self.l1_ratio_ = best_l1_ratio
        self.alpha_ = best_alpha
        if self.alphas is None:
            self.alphas_ = np.asarray(alphas)
            if n_l1_ratio == 1:
                self.alphas_ = self.alphas_[0]
        # Remove duplicate alphas in case alphas is provided.
        else:
            self.alphas_ = np.asarray(alphas[0])

        # Refit the model with the parameters selected
        common_params = dict((name, value)
                             for name, value in self.get_params().items()
                             if name in model.get_params())
        model.set_params(**common_params)
        model.alpha = best_alpha
        model.l1_ratio = best_l1_ratio
        model.copy_X = copy_X
        model.fit(X, y)
        if not hasattr(self, 'l1_ratio'):
            del self.l1_ratio_
        self.coef_ = model.coef_
        self.intercept_ = model.intercept_
        self.dual_gap_ = model.dual_gap_
        return self