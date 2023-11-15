    def result(self):
        model_cls = self._cmd.get_models(self._model_type)
        return model_cls.deserialize(self._payload)