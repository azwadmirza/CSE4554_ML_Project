    def _save_top_k_checkpoints(self, trainer, pl_module, metrics):
        current = metrics.get(self.monitor)
        epoch = metrics.get("epoch")
        step = metrics.get("step")

        if not isinstance(current, torch.Tensor) and current is not None:
            current = torch.tensor(current, device=pl_module.device)

        if self.check_monitor_top_k(current):
            self._update_best_and_save(current, epoch, step, trainer, pl_module, metrics)
        elif self.verbose:
            rank_zero_info(
                f"Epoch {epoch:d}, step {step:d}: {self.monitor} was not in top {self.save_top_k}"
            )