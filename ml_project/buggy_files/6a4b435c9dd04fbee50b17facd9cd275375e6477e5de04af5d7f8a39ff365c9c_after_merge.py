    def temperature_model(self, model):
        if model is None:
            self._temperature_model = self.infer_temperature_model()
        elif isinstance(model, str):
            model = model.lower()
            if model == 'sapm':
                self._temperature_model = self.sapm_temp
            elif model == 'pvsyst':
                self._temperature_model = self.pvsyst_temp
            elif model == 'faiman':
                self._temperature_model = self.faiman_temp
            elif model == 'fuentes':
                self._temperature_model = self.fuentes_temp
            else:
                raise ValueError(model + ' is not a valid temperature model')
            # check system.temperature_model_parameters for consistency
            name_from_params = self.infer_temperature_model().__name__
            if self._temperature_model.__name__ != name_from_params:
                raise ValueError(
                    'Temperature model {} is inconsistent with '
                    'PVsystem.temperature_model_parameters {}'.format(
                        self._temperature_model.__name__,
                        self.system.temperature_model_parameters))
        else:
            self._temperature_model = partial(model, self)