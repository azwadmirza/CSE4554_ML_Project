    def __init__(self, preprocessors=None, **kwargs):
        super().__init__(**kwargs)
        self.preprocessors = nest.flatten(preprocessors)
        self._finished = False
        # Save or load the HyperModel.
        self.hypermodel.hypermodel.save(os.path.join(self.project_dir, 'graph'))