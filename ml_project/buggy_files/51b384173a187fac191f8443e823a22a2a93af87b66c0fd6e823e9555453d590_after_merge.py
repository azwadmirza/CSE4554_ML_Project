    def __init__(self, path_context: str, label: str, id_columns: list, feature_generator: PipelineFeatureGenerator, label_count_threshold=10,
                 problem_type=None, eval_metric=None, stopping_metric=None, is_trainer_present=False, random_seed=0):
        self.path, self.model_context, self.save_path = self.create_contexts(path_context)
        self.label = label
        self.id_columns = id_columns
        self.threshold = label_count_threshold
        self.problem_type = problem_type
        self.eval_metric = eval_metric
        self.stopping_metric = stopping_metric
        self.is_trainer_present = is_trainer_present
        if random_seed is None:
            random_seed = random.randint(0, 1000000)
        self.random_seed = random_seed
        self.cleaner = None
        self.label_cleaner: LabelCleaner = None
        self.feature_generator: PipelineFeatureGenerator = feature_generator
        self.feature_generators = [self.feature_generator]

        self.trainer: AbstractTrainer = None
        self.trainer_type = None
        self.trainer_path = None
        self.reset_paths = False

        self.time_fit_total = None
        self.time_fit_preprocessing = None
        self.time_fit_training = None
        self.time_limit = None

        try:
            from .....version import __version__
            self.version = __version__
        except:
            self.version = None