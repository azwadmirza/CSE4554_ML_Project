    def unregister_predictor(self, name):
        for integration in self._get_integrations():
            if integration.check_connection():
                integration.unregister_predictor(name)
            else:
                logger.warning(f"There is no connection to {integration.name}. predictor wouldn't be unregistred")