    def infer_temperature_model(self):
        """Infer temperature model from system attributes."""
        params = set(self.system.temperature_model_parameters.keys())
        # remove or statement in v0.9
        if {'a', 'b', 'deltaT'} <= params or (
                not params and self.system.racking_model is None
                and self.system.module_type is None):
            return self.sapm_temp
        elif {'u_c', 'u_v'} <= params:
            return self.pvsyst_temp
        elif {'u0', 'u1'} <= params:
            return self.faiman_temp
        elif {'noct_installed'} <= params:
            return self.fuentes_temp
        else:
            raise ValueError('could not infer temperature model from '
                             'system.temperature_module_parameters {}.'
                             .format(self.system.temperature_model_parameters))