    def __init__(self, preprocessors=None, **kwargs):
        super().__init__(**kwargs)
        self.preprocessors = nest.flatten(preprocessors)
        self._finished = False
        # Save or load the HyperModel.
        utils.save_json(os.path.join(self.project_dir, 'graph'),
                        graph_module.serialize(self.hypermodel.hypermodel))