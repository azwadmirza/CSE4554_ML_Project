    def unregister_predictor(self, name):
        for integration in self._get_integrations():
            integration.unregister_predictor(name)