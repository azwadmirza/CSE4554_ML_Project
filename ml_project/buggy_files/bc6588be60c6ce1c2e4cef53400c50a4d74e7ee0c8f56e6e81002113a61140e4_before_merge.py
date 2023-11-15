        def on_epoch_end(self, epoch, logs=None):
            if not logs:
                return
            try:
                mlflow.log_metrics(logs, step=epoch)
            except mlflow.exceptions.MlflowException as e:
                warnings.warn("Logging to MLflow failed: " + str(e))