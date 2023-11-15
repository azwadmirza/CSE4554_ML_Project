    def run_training_epoch_end(self, epoch_output):
        model = self.get_model()
        if self.is_overridden('training_epoch_end', model=model):
            self.global_step += 1
            epoch_output = model.training_epoch_end(epoch_output)
            _processed_outputs = self.process_output(epoch_output)
            log_epoch_metrics = _processed_outputs[2]
            callback_epoch_metrics = _processed_outputs[3]

            # add the metrics to the loggers
            self.log_metrics(log_epoch_metrics, {})

            # add metrics to callbacks
            self.callback_metrics.update(callback_epoch_metrics)

            # add metrics to progress_bar
            self.add_progress_bar_metrics(_processed_outputs[1])