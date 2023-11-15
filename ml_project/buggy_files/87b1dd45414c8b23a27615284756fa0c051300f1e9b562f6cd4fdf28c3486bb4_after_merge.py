    def export_autokeras_model(self, model_file_name):
        """ Creates and Exports the AutoKeras model to the given filename. """
        portable_model = PortableImageSupervised(graph=self.cnn.best_model,
                                                 y_encoder=self.y_encoder,
                                                 data_transformer=self.data_transformer,
                                                 metric=self.metric,
                                                 inverse_transform_y_method=self.inverse_transform_y,
                                                 resize_params=(self.resize_height, self.resize_width))
        pickle_to_file(portable_model, model_file_name)