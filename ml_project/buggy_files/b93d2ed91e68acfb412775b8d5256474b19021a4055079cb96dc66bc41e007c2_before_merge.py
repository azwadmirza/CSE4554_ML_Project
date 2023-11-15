    def __init__(self, learner):
        """ Creates TabularPredictor object.
            You should not construct a TabularPredictor yourself, it is only intended to be produced during fit().

            Parameters
            ----------
            learner : `AbstractLearner` object
                Object that implements the `AbstractLearner` APIs.

            To access any learner method `func()` from this Predictor, use: `predictor._learner.func()`.
            To access any trainer method `func()` from this `Predictor`, use: `predictor._trainer.func()`.
        """
        self._learner: Learner = learner  # Learner object
        self._learner.persist_trainer(low_memory=True)
        self._trainer: AbstractTrainer = self._learner.load_trainer()  # Trainer object
        self.output_directory = self._learner.path
        self.problem_type = self._learner.problem_type
        self.eval_metric = self._learner.eval_metric
        self.label_column = self._learner.label
        self.feature_types = self._trainer.feature_types_metadata
        self.class_labels = self._learner.class_labels
        self.class_labels_internal = self._learner.label_cleaner.ordered_class_labels_transformed
        self.class_labels_internal_map = self._learner.label_cleaner.inv_map