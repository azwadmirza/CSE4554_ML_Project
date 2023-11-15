    def total_train_batches(self) -> int:
        """
        The total number of training batches during training, which may change from epoch to epoch.
        Use this to set the total number of iterations in the progress bar. Can return ``inf`` if the
        training dataloader is of infinite size.
        """
        total_train_batches = 1 if self.trainer.fast_dev_run else self.trainer.num_training_batches
        return total_train_batches