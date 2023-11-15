    def total_val_batches(self) -> int:
        """
        The total number of training batches during validation, which may change from epoch to epoch.
        Use this to set the total number of iterations in the progress bar. Can return ``inf`` if the
        validation dataloader is of infinite size.
        """
        trainer = self.trainer
        total_val_batches = 0
        if trainer.fast_dev_run and trainer.val_dataloaders is not None:
            total_val_batches = len(trainer.val_dataloaders)
        elif self.trainer.enable_validation:
            is_val_epoch = (trainer.current_epoch + 1) % trainer.check_val_every_n_epoch == 0
            total_val_batches = sum(trainer.num_val_batches) if is_val_epoch else 0
        return total_val_batches