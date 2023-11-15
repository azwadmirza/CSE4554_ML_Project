    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._model_type = self._get_model_type()
        self._feature_generator = None