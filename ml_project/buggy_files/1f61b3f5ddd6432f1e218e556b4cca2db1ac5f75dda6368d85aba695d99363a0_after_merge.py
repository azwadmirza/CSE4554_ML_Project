    def on_train_end(self, logs=None):  # pylint: disable=unused-argument
        opt = self.model.optimizer
        if hasattr(opt, 'optimizer'):
            opt = opt.optimizer
            try_mlflow_log(mlflow.log_param, 'optimizer_name', type(opt).__name__)
        if hasattr(opt, '_lr'):
            lr = opt._lr if type(opt._lr) is float else tensorflow.keras.backend.eval(opt._lr)
            try_mlflow_log(mlflow.log_param('learning_rate', lr))
        if hasattr(opt, '_epsilon'):
            epsilon = opt._epsilon if type(opt._epsilon) is float \
                else tensorflow.keras.backend.eval(opt._epsilon)
            try_mlflow_log(mlflow.log_param, 'epsilon', epsilon)
        l = []
        self.model.summary(print_fn=l.append)
        summary = '\n'.join(l)
        try_mlflow_log(mlflow.set_tag, 'summary', summary)
        try_mlflow_log(mlflow.keras.log_model, self.model, artifact_path='model')