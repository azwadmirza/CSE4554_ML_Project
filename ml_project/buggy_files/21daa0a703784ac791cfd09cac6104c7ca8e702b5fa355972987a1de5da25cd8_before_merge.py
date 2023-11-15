    def convert_to_refitfull_template(self):
        compressed_params = self._get_compressed_params()
        model_compressed = copy.deepcopy(self._get_model_base())
        model_compressed.feature_types_metadata = self.feature_types_metadata  # TODO: Don't pass this here
        model_compressed.params = compressed_params
        model_compressed.name = model_compressed.name + REFIT_FULL_SUFFIX
        model_compressed.set_contexts(self.path_root + model_compressed.name + os.path.sep)
        return model_compressed