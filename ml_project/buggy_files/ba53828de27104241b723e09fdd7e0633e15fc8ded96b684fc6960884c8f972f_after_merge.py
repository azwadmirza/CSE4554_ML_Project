    def train(
        self,
        n_epochs: int = 400,
        train_size: float = 0.9,
        test_size: Optional[float] = None,
        lr: float = 4e-3,
        n_epochs_kl_warmup: Optional[int] = None,
        n_iter_kl_warmup: Union[Literal["auto"], int] = "auto",
        batch_size: int = 256,
        frequency: Optional[int] = None,
        train_fun_kwargs: dict = {},
        **kwargs,
    ):
        """
        Train the model.

        Parameters
        ----------
        n_epochs
            Number of passes through the dataset.
        train_size
            Size of training set in the range [0.0, 1.0].
        test_size
            Size of the test set. If `None`, defaults to 1 - `train_size`. If
            `train_size + test_size < 1`, the remaining cells belong to a validation set.
        lr
            Learning rate for optimization.
        n_epochs_kl_warmup
            Number of passes through dataset for scaling term on KL divergence to go from 0 to 1.
        n_iter_kl_warmup
            Number of minibatches for scaling term on KL divergence to go from 0 to 1.
            To use, set to not `None` and set `n_epochs_kl_warmup` to `None`.
        batch_size
            Minibatch size to use during training.
        frequency
            Frequency with which metrics are computed on the data for train/test/val sets.
        train_fun_kwargs
            Keyword args for the train method of :class:`~scvi.core.trainers.TotalTrainer`.
        **kwargs
            Other keyword args for :class:`~scvi.core.trainers.TotalTrainer`.
        """
        train_fun_kwargs = dict(train_fun_kwargs)
        if "totalvi_batch_mask" in self.scvi_setup_dict_.keys():
            imputation = True
        else:
            imputation = False
        self.trainer = TotalTrainer(
            self.model,
            self.adata,
            train_size=train_size,
            test_size=test_size,
            n_iter_kl_warmup=n_iter_kl_warmup,
            n_epochs_kl_warmup=n_epochs_kl_warmup,
            frequency=frequency,
            batch_size=batch_size,
            use_adversarial_loss=imputation,
            use_cuda=self.use_cuda,
            **kwargs,
        )
        # for autotune
        if "n_epochs" not in train_fun_kwargs:
            train_fun_kwargs["n_epochs"] = n_epochs
        if "lr" not in train_fun_kwargs:
            train_fun_kwargs["lr"] = lr

        logger.info("Training for {} epochs.".format(n_epochs))

        self.trainer.train(**train_fun_kwargs)
        self.is_trained_ = True
        self.train_indices_ = self.trainer.train_set.indices
        self.test_indices_ = self.trainer.test_set.indices
        self.validation_indices_ = self.trainer.validation_set.indices
        self.history_ = self.trainer.history