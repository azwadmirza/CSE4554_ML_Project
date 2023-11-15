    def register_predictors(self, model_data_arr, setup=True):
        it = self._get_integrations()
        for integration in it:
            register = True
            if setup:
                register = self._setup_integration(integration)
            if register:
                integration.register_predictors(model_data_arr)

            integration = [integration]