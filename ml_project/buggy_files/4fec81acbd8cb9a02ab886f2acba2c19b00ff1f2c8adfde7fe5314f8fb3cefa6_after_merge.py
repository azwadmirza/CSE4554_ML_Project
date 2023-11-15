    def __getstate__(self):
        state = self.__dict__.copy()

        # Experiment cannot be pickled, and additionally its ID cannot be pickled in offline mode
        state['_experiment'] = None
        if self.offline_mode:
            state['_experiment_id'] = None

        return state