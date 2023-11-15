    def set_results(self, results):
        """Set the input results."""
        # false positive, pylint: disable=no-member
        prev_sel_learner = self.selected_learner.copy()
        self.clear()
        self.warning()
        self.closeContext()

        data = None
        if results is not None and results.data is not None:
            data = results.data[results.row_indices]

        if data is not None and not data.domain.has_discrete_class:
            self.Error.no_regression()
            data = results = None
        else:
            self.Error.no_regression.clear()

        nan_values = False
        if results is not None:
            assert isinstance(results, Orange.evaluation.Results)
            if np.any(np.isnan(results.actual)) or \
                    np.any(np.isnan(results.predicted)):
                # Error out here (could filter them out with a warning
                # instead).
                nan_values = True
                results = data = None

        self.Error.invalid_values(shown=nan_values)

        self.results = results
        self.data = data

        if data is not None:
            class_values = data.domain.class_var.values
        elif results is not None:
            raise NotImplementedError

        if results is None:
            self.report_button.setDisabled(True)
            return

        self.report_button.setDisabled(False)

        nmodels = results.predicted.shape[0]
        self.headers = class_values + \
                       [unicodedata.lookup("N-ARY SUMMATION")]

        # NOTE: The 'learner_names' is set in 'Test Learners' widget.
        self.learners = getattr(
            results, "learner_names",
            [f"Learner #{i + 1}" for i in range(nmodels)])

        self._init_table(len(class_values))
        self.openContext(data.domain.class_var)
        if not prev_sel_learner or prev_sel_learner[0] >= len(self.learners):
            if self.learners:
                self.selected_learner[:] = [0]
        else:
            self.selected_learner[:] = prev_sel_learner
        self._update()
        self._set_selection()
        self.unconditional_commit()