    def _update(self, model):
        if self.object is None:
            json = None
        else:
            json = self._to_json(self.object)
            self._get_sources(json, model.data_sources)
        model.data = json