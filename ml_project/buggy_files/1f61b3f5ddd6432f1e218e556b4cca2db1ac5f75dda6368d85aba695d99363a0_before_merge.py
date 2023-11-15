    def on_train_end(self, logs=None):  # pylint: disable=unused-argument
        opt = self.model.optimizer
        if hasattr(opt, 'optimizer'):
            opt = opt.optimizer
        mlflow.log_param('optimizer_name', type(opt).__name__)
        if hasattr(opt, '_lr'):
            lr = opt._lr if type(opt._lr) is float else tensorflow.keras.backend.eval(opt._lr)
            mlflow.log_param('learning_rate', lr)
        if hasattr(opt, '_epsilon'):
            epsilon = opt._epsilon if type(opt._epsilon) is float \
                else tensorflow.keras.backend.eval(opt._epsilon)
            mlflow.log_param('epsilon', epsilon)
        l = []
        self.model.summary(print_fn=l.append)
        summary = '\n'.join(l)
        mlflow.set_tag('summary', summary)
        mlflow.keras.log_model(self.model, artifact_path='model')