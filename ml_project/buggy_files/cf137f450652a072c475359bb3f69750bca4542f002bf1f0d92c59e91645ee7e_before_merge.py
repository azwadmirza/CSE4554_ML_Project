def autolog():
    """
    Enable automatic logging from TensorFlow to MLflow.
    Logs loss and any other metrics specified in the fit
    function, and optimizer data as parameters. Model checkpoints
    are logged as artifacts to a 'models' directory.
    """
    import keras

    class __MLflowKerasCallback(keras.callbacks.Callback):
        """
        Callback for auto-logging metrics and parameters.
        Records available logs after each epoch.
        Records model structural information as params after training finishes.
        """

        def on_epoch_end(self, epoch, logs=None):
            if not logs:
                return
            try:
                mlflow.log_metrics(logs, step=epoch)
            except mlflow.exceptions.MlflowException as e:
                warnings.warn("Logging to MLflow failed: " + str(e))

        def on_train_end(self, logs=None):
            try:
                mlflow.log_param('num_layers', len(self.model.layers))
                mlflow.log_param('optimizer_name', type(self.model.optimizer).__name__)
                if hasattr(self.model.optimizer, 'lr'):
                    lr = self.model.optimizer.lr if \
                        type(self.model.optimizer.lr) is float \
                        else keras.backend.eval(self.model.optimizer.lr)
                    mlflow.log_param('learning_rate', lr)
                if hasattr(self.model.optimizer, 'epsilon'):
                    epsilon = self.model.optimizer.epsilon if \
                        type(self.model.optimizer.epsilon) is float \
                        else keras.backend.eval(self.model.optimizer.epsilon)
                    mlflow.log_param('epsilon', epsilon)
                sum_list = []
                self.model.summary(print_fn=sum_list.append)
                summary = '\n'.join(sum_list)
                mlflow.set_tag('summary', summary)
                log_model(self.model, artifact_path='model')
            except mlflow.exceptions.MlflowException as e:
                warnings.warn("Logging to Mlflow failed: " + str(e))

    @gorilla.patch(keras.Model)
    def fit(self, *args, **kwargs):
        original = gorilla.get_original_attribute(keras.Model, 'fit')
        if len(args) >= 6:
            l = list(args)
            l[5] += [__MLflowKerasCallback()]
            args = tuple(l)
        elif 'callbacks' in kwargs:
            kwargs['callbacks'] += [__MLflowKerasCallback()]
        else:
            kwargs['callbacks'] = [__MLflowKerasCallback()]
        return original(self, *args, **kwargs)
    settings = gorilla.Settings(allow_hit=True, store_hit=True)
    patch = gorilla.Patch(keras.Model, 'fit', fit, settings=settings)
    gorilla.apply(patch)