    def _run_early_stopping_check(self, trainer, pl_module):
        logs = trainer.callback_metrics
        if not self._validate_condition_metric(logs):
            return  # short circuit if metric not present

        current = logs.get(self.monitor)
        if not isinstance(current, torch.Tensor):
            current = torch.tensor(current)

        if self.monitor_op(current - self.min_delta, self.best_score):
            self.best_score = current
            self.wait_count = 0
        else:
            self.wait_count += 1
            if self.wait_count >= self.patience:
                self.stopped_epoch = trainer.current_epoch
                trainer.should_stop = True