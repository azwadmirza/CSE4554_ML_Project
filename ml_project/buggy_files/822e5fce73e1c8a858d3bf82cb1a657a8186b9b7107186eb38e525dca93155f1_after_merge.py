    def result(self):
        module = import_module(self._model_path)
        model_cls = getattr(module, self._model_name)
        return model_cls.deserialize(self._payload)