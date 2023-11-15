    def __init__(self, path: str, problem_type: str, scheduler_options=None, eval_metric=None, stopping_metric=None,
                 num_classes=None, low_memory=False, feature_types_metadata=None, kfolds=0, n_repeats=1,
                 stack_ensemble_levels=0, time_limit=None, save_data=False, save_bagged_folds=True, random_seed=0, verbosity=2):
        self.path = path
        self.problem_type = problem_type
        self.feature_types_metadata = feature_types_metadata
        self.save_data = save_data
        self.random_seed = random_seed  # Integer value added to the stack level to get the random_seed for kfold splits or the train/val split if bagging is disabled
        self.verbosity = verbosity
        if eval_metric is not None:
            self.eval_metric = eval_metric
        else:
            self.eval_metric = infer_eval_metric(problem_type=self.problem_type)

        # stopping_metric is used to early stop all models except for aux models.
        if stopping_metric is not None:
            self.stopping_metric = stopping_metric
        elif self.eval_metric.name == 'roc_auc':
            self.stopping_metric = log_loss
        else:
            self.stopping_metric = self.eval_metric

        self.eval_metric_expects_y_pred = scorer_expects_y_pred(scorer=self.eval_metric)
        logger.log(25, "AutoGluon will gauge predictive performance using evaluation metric: %s" % self.eval_metric.name)
        if not self.eval_metric_expects_y_pred:
            logger.log(25, "This metric expects predicted probabilities rather than predicted class labels, so you'll need to use predict_proba() instead of predict()")

        logger.log(20, "To change this, specify the eval_metric argument of fit()")
        logger.log(25, "AutoGluon will early stop models using evaluation metric: %s" % self.stopping_metric.name)
        self.num_classes = num_classes
        self.feature_prune = False # will be set to True if feature-pruning is turned on.
        self.low_memory = low_memory
        self.bagged_mode = True if kfolds >= 2 else False
        if self.bagged_mode:
            self.kfolds = kfolds  # int number of folds to do model bagging, < 2 means disabled
            self.stack_ensemble_levels = stack_ensemble_levels
            self.stack_mode = True if self.stack_ensemble_levels >= 1 else False
            self.n_repeats = n_repeats
        else:
            self.kfolds = 0
            self.stack_ensemble_levels = 0
            self.stack_mode = False
            self.n_repeats = 1
        self.save_bagged_folds = save_bagged_folds

        self.hyperparameters = {}  # TODO: This is currently required for fetching stacking layer models. Consider incorporating more elegantly

        # self.models_level_all['core'][0] # Includes base models
        # self.models_level_all['core'][1] # Stacker level 1
        # self.models_level_all['aux1'][1] # Stacker level 1 aux models, such as weighted_ensemble
        # self.models_level_all['core'][2] # Stacker level 2
        self.models_level = defaultdict(dd_list)

        self.model_best = None

        self.model_performance = {}  # TODO: Remove in future, use networkx.
        self.model_paths = {}
        self.model_types = {}  # Outer type, can be BaggedEnsemble, StackEnsemble (Type that is able to load the model)
        self.model_types_inner = {}  # Inner type, if Ensemble then it is the type of the inner model (May not be able to load with this type)
        self.models = {}
        self.model_graph = nx.DiGraph()
        self.model_full_dict = {}  # Dict of normal Model -> FULL Model
        self.reset_paths = False

        self.hpo_results = {}  # Stores summary of HPO process
        # Scheduler attributes:
        if scheduler_options is not None:
            self.scheduler_func = scheduler_options[0]  # unpack tuple
            self.scheduler_options = scheduler_options[1]
        else:
            self.scheduler_func = None
            self.scheduler_options = None

        self.time_limit = time_limit
        if self.time_limit is None:
            self.time_limit = 1e7
            self.ignore_time_limit = True
        else:
            self.ignore_time_limit = False
        self.time_train_start = None
        self.time_train_level_start = None
        self.time_limit_per_level = self.time_limit / (self.stack_ensemble_levels + 1)

        self.num_rows_train = None
        self.num_cols_train = None

        self.is_data_saved = False

        self.regress_preds_asprobas = False  # whether to treat regression predictions as class-probabilities (during distillation)