        def on_train_end(self, logs=None):
            try_mlflow_log(mlflow.log_param, 'num_layers', len(self.model.layers))
            try_mlflow_log(mlflow.log_param, 'optimizer_name', type(self.model.optimizer).__name__)
            if hasattr(self.model.optimizer, 'lr'):
                lr = self.model.optimizer.lr if \
                    type(self.model.optimizer.lr) is float \
                    else keras.backend.eval(self.model.optimizer.lr)
                try_mlflow_log(mlflow.log_param, 'learning_rate', lr)
            if hasattr(self.model.optimizer, 'epsilon'):
                epsilon = self.model.optimizer.epsilon if \
                    type(self.model.optimizer.epsilon) is float \
                    else keras.backend.eval(self.model.optimizer.epsilon)
                try_mlflow_log(mlflow.log_param, 'epsilon', epsilon)
            sum_list = []
            self.model.summary(print_fn=sum_list.append)
            summary = '\n'.join(sum_list)
            try_mlflow_log(mlflow.set_tag, 'summary', summary)
            try_mlflow_log(log_model, self.model, artifact_path='model')