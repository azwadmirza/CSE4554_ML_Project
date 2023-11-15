    def __init__(self, model_base: AbstractModel, save_bagged_folds=True, random_state=0, **kwargs):
        self.model_base = model_base
        self._child_type = type(self.model_base)
        self.models = []
        self._oof_pred_proba = None
        self._oof_pred_model_repeats = None
        self._n_repeats = 0  # Number of n_repeats with at least 1 model fit, if kfold=5 and 8 models have been fit, _n_repeats is 2
        self._n_repeats_finished = 0  # Number of n_repeats finished, if kfold=5 and 8 models have been fit, _n_repeats_finished is 1
        self._k_fold_end = 0  # Number of models fit in current n_repeat (0 if completed), if kfold=5 and 8 models have been fit, _k_fold_end is 3
        self._k = None  # k models per n_repeat, equivalent to kfold value
        self._k_per_n_repeat = []  # k-fold used for each n_repeat. == [5, 10, 3] if first kfold was 5, second was 10, and third was 3
        self._random_state = random_state
        self.low_memory = True
        self.bagged_mode = None
        self.save_bagged_folds = save_bagged_folds

        try:
            feature_types_metadata = self.model_base.feature_types_metadata
        except:
            feature_types_metadata = None

        eval_metric = kwargs.pop('eval_metric', self.model_base.eval_metric)
        stopping_metric = kwargs.pop('stopping_metric', self.model_base.stopping_metric)

        super().__init__(problem_type=self.model_base.problem_type, eval_metric=eval_metric, stopping_metric=stopping_metric, feature_types_metadata=feature_types_metadata, **kwargs)