    def export_saved_model(self, *args, **kwargs):
        original = gorilla.get_original_attribute(tensorflow.estimator.Estimator,
                                                  'export_saved_model')
        serialized = original(self, *args, **kwargs)
        try_mlflow_log(log_model, tf_saved_model_dir=serialized.decode('utf-8'),
                       tf_meta_graph_tags=[tag_constants.SERVING],
                       tf_signature_def_key='predict',
                       artifact_path='model')
        return serialized