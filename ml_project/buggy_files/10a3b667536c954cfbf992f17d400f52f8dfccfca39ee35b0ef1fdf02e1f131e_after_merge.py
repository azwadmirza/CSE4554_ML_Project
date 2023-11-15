    def _run_early_stopping_check(self, trainer, pl_module):
        logs = trainer.callback_metrics
        if not self._validate_condition_metric(logs):
            return  # short circuit if metric not present

        current = logs.get(self.monitor)
        if not isinstance(current, torch.Tensor):
            current = torch.tensor(current, device=pl_module.device)

        if self.monitor_op(current - self.min_delta, self.best_score.to(pl_module.device)):
            self.best_score = current
            self.wait_count = 0
        else:
            self.wait_count += 1
            should_stop = self.wait_count >= self.patience

            if bool(should_stop):
                self.stopped_epoch = trainer.current_epoch
                trainer.should_stop = True

        # stop every ddp process if any world process decides to stop
        self._stop_distributed_training(trainer, pl_module)