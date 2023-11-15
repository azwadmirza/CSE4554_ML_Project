    def _set_default_auxiliary_params(self):
        default_auxiliary_params = dict(
            ignored_feature_types_special=['text_ngram', 'text_as_category'],
        )
        for key, value in default_auxiliary_params.items():
            self._set_default_param_value(key, value, params=self.params_aux)
        super()._set_default_auxiliary_params()