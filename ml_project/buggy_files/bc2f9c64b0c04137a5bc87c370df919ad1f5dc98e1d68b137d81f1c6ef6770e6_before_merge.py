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