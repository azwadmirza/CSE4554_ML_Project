    def __getstate__(self):
        state = self.__dict__.copy()
        # cannot be pickled
        state['_experiment'] = None
        # args needed to reload correct experiment
        state['_id'] = self.experiment.id
        return state