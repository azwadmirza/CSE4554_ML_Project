    def total_val_batches(self) -> int:
        """
        The total number of training batches during validation, which may change from epoch to epoch.
        Use this to set the total number of iterations in the progress bar. Can return ``inf`` if the
        validation dataloader is of infinite size.
        """
        total_val_batches = 0
        if not self.trainer.disable_validation:
            is_val_epoch = (self.trainer.current_epoch + 1) % self.trainer.check_val_every_n_epoch == 0
            total_val_batches = sum(self.trainer.num_val_batches) if is_val_epoch else 0
        return total_val_batches