    def __init__(self, path: str, name: str, problem_type: str, eval_metric: Union[str, metrics.Scorer] = None, num_classes=None, stopping_metric=None, model=None, hyperparameters=None, features=None, feature_types_metadata: FeatureTypesMetadata = None, debug=0, **kwargs):
        """ Creates a new model.
            Args:
                path (str): directory where to store all outputs.
                name (str): name of subdirectory inside path where model will be saved.
                problem_type (str): type of problem this model will handle. Valid options: ['binary', 'multiclass', 'regression'].
                eval_metric (str or autogluon.utils.tabular.metrics.Scorer): objective function the model intends to optimize. If None, will be inferred based on problem_type.
                hyperparameters (dict): various hyperparameters that will be used by model (can be search spaces instead of fixed values).
                feature_types_metadata (autogluon.utils.tabular.features.feature_types_metadata.FeatureTypesMetadata): contains feature type information that can be used to identify special features such as text ngrams and datetime.
        """
        self.name = name
        self.path_root = path
        self.path_suffix = self.name + os.path.sep  # TODO: Make into function to avoid having to reassign on load?
        self.path = self.create_contexts(self.path_root + self.path_suffix)  # TODO: Make this path a function for consistency.
        self.num_classes = num_classes
        self.model = model
        self.problem_type = problem_type
        if eval_metric is not None:
            self.eval_metric = metrics.get_metric(eval_metric, self.problem_type, 'eval_metric')  # Note: we require higher values = better performance
        else:
            self.eval_metric = infer_eval_metric(problem_type=self.problem_type)
            logger.log(20, f"Model {self.name}'s eval_metric inferred to be '{self.eval_metric.name}' because problem_type='{self.problem_type}' and eval_metric was not specified during init.")

        if stopping_metric is None:
            self.stopping_metric = self.eval_metric
        else:
            self.stopping_metric = stopping_metric

        if self.eval_metric.name in OBJECTIVES_TO_NORMALIZE:
            self.normalize_pred_probas = True
            logger.debug(self.name +" predicted probabilities will be transformed to never =0 since eval_metric=" + self.eval_metric.name)
        else:
            self.normalize_pred_probas = False

        if isinstance(self.eval_metric, metrics._ProbaScorer):
            self.metric_needs_y_pred = False
        elif isinstance(self.eval_metric, metrics._ThresholdScorer):
            self.metric_needs_y_pred = False
        else:
            self.metric_needs_y_pred = True

        if isinstance(self.stopping_metric, metrics._ProbaScorer):
            self.stopping_metric_needs_y_pred = False
        elif isinstance(self.stopping_metric, metrics._ThresholdScorer):
            self.stopping_metric_needs_y_pred = False
        else:
            self.stopping_metric_needs_y_pred = True

        self.feature_types_metadata = feature_types_metadata  # TODO: Should this be passed to a model on creation? Should it live in a Dataset object and passed during fit? Currently it is being updated prior to fit by trainer
        self.features = features
        self.debug = debug

        self.fit_time = None  # Time taken to fit in seconds (Training data)
        self.predict_time = None  # Time taken to predict in seconds (Validation data)
        self.val_score = None  # Score with eval_metric (Validation data)

        self.params = {}
        self.params_aux = {}

        self._set_default_auxiliary_params()
        if hyperparameters is not None:
            hyperparameters = hyperparameters.copy()
            if AG_ARGS_FIT in hyperparameters:
                ag_args_fit = hyperparameters.pop(AG_ARGS_FIT)
                self.params_aux.update(ag_args_fit)
        self._set_default_params()
        self.nondefault_params = []
        if hyperparameters is not None:
            self.params.update(hyperparameters)
            self.nondefault_params = list(hyperparameters.keys())[:]  # These are hyperparameters that user has specified.
        self.params_trained = dict()