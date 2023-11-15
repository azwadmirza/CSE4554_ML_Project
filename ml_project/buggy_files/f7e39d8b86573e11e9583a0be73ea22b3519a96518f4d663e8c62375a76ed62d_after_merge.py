    def _set_default_auxiliary_params(self):
        default_auxiliary_params = dict(
            ignored_type_group_raw=[R_CATEGORY, R_OBJECT],  # TODO: Eventually use category features
            ignored_type_group_special=[S_TEXT_NGRAM, S_TEXT_SPECIAL, S_DATETIME_AS_INT],
        )
        for key, value in default_auxiliary_params.items():
            self._set_default_param_value(key, value, params=self.params_aux)
        super()._set_default_auxiliary_params()