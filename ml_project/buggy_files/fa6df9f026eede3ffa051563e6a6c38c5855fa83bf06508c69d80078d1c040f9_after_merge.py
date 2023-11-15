    def fit(self, X, y, **kwargs):
        """Run the grid search.

        This will result in multiple copies of the
        estimator being made, and the :code:`fit(X)` method
        of each one called.

        :param X: The feature matrix
        :type X: numpy.ndarray or pandas.DataFrame

        :param y: The label vector
        :type y: numpy.ndarray, pandas.DataFrame, pandas.Series, or list

        :param sensitive_features: A (currently) required keyword argument listing the
            feature used by the constraints object
        :type sensitive_features: numpy.ndarray, pandas.DataFrame, pandas.Series, or list (for now)
        """
        if isinstance(self.constraints, ClassificationMoment):
            logger.debug("Classification problem detected")
            is_classification_reduction = True
        else:
            logger.debug("Regression problem detected")
            is_classification_reduction = False

        _, y_train, sensitive_features_train = _validate_and_reformat_input(
            X, y, enforce_binary_labels=is_classification_reduction, **kwargs)

        kwargs[_KW_SENSITIVE_FEATURES] = sensitive_features_train

        # Prep the parity constraints and objective
        logger.debug("Preparing constraints and objective")
        self.constraints.load_data(X, y_train, **kwargs)
        objective = self.constraints.default_objective()
        objective.load_data(X, y_train, **kwargs)

        # Basis information
        pos_basis = self.constraints.pos_basis
        neg_basis = self.constraints.neg_basis
        neg_allowed = self.constraints.neg_basis_present
        objective_in_the_span = (self.constraints.default_objective_lambda_vec is not None)

        if self.grid is None:
            logger.debug("Creating grid of size %i", self.grid_size)
            grid = _GridGenerator(self.grid_size,
                                  self.grid_limit,
                                  pos_basis,
                                  neg_basis,
                                  neg_allowed,
                                  objective_in_the_span,
                                  self.grid_offset).grid
        else:
            logger.debug("Using supplied grid")
            grid = self.grid

        # Fit the estimates
        logger.debug("Setup complete. Starting grid search")
        for i in grid.columns:
            lambda_vec = grid[i]
            logger.debug("Obtaining weights")
            weights = self.constraints.signed_weights(lambda_vec)
            if not objective_in_the_span:
                weights = weights + objective.signed_weights()

            if is_classification_reduction:
                logger.debug("Applying relabelling for classification problem")
                y_reduction = 1 * (weights > 0)
                weights = weights.abs()
            else:
                y_reduction = y_train

            y_reduction_unique = np.unique(y_reduction)
            if len(y_reduction_unique) == 1:
                logger.debug("y_reduction had single value. Using DummyClassifier")
                current_estimator = DummyClassifier(strategy='constant',
                                                    constant=y_reduction_unique[0])
            else:
                logger.debug("Using underlying estimator")
                current_estimator = copy.deepcopy(self.estimator)

            oracle_call_start_time = time()
            current_estimator.fit(X, y_reduction, sample_weight=weights)
            oracle_call_execution_time = time() - oracle_call_start_time
            logger.debug("Call to estimator complete")

            def predict_fct(X): return current_estimator.predict(X)
            self._predictors.append(current_estimator)
            self._lambda_vecs[i] = lambda_vec
            self._objectives.append(objective.gamma(predict_fct)[0])
            self._gammas[i] = self.constraints.gamma(predict_fct)
            self._oracle_execution_times.append(oracle_call_execution_time)

        logger.debug("Selecting best_result")
        if self.selection_rule == TRADEOFF_OPTIMIZATION:
            def loss_fct(i):
                return self.objective_weight * self._objectives[i] + \
                    self.constraint_weight * self._gammas[i].max()
            losses = [loss_fct(i) for i in range(len(self._objectives))]
            self._best_grid_index = losses.index(min(losses))
        else:
            raise RuntimeError("Unsupported selection rule")

        return