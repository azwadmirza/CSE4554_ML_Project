    def train(
        self,
        n_epochs_unsupervised: Optional[int] = None,
        n_epochs_semisupervised: Optional[int] = None,
        train_size: float = 0.9,
        test_size: float = None,
        lr: float = 1e-3,
        n_epochs_kl_warmup: int = 400,
        n_iter_kl_warmup: Optional[int] = None,
        frequency: Optional[int] = None,
        unsupervised_trainer_kwargs: dict = {},
        semisupervised_trainer_kwargs: dict = {},
        unsupervised_train_kwargs: dict = {},
        semisupervised_train_kwargs: dict = {},
    ):
        """
        Train the model.

        Parameters
        ----------
        n_epochs_unsupervised
            Number of passes through the dataset for unsupervised pre-training.
        n_epochs_semisupervised
            Number of passes through the dataset for semisupervised training.
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
        frequency
            Frequency with which metrics are computed on the data for train/test/val sets for both
            the unsupervised and semisupervised trainers. If you'd like a different frequency for
            the semisupervised trainer, set frequency in semisupervised_train_kwargs.
        unsupervised_trainer_kwargs
            Other keyword args for :class:`~scvi.core.trainers.UnsupervisedTrainer`.
        semisupervised_trainer_kwargs
            Other keyword args for :class:`~scvi.core.trainers.SemiSupervisedTrainer`.
        semisupervised_train_kwargs
            Keyword args for the train method of :class:`~scvi.core.trainers.SemiSupervisedTrainer`.
        """
        unsupervised_trainer_kwargs = dict(unsupervised_trainer_kwargs)
        semisupervised_trainer_kwargs = dict(semisupervised_trainer_kwargs)
        unsupervised_train_kwargs = dict(unsupervised_train_kwargs)
        semisupervised_train_kwargs = dict(semisupervised_train_kwargs)

        if n_epochs_unsupervised is None:
            n_epochs_unsupervised = np.min(
                [round((20000 / self.adata.shape[0]) * 400), 400]
            )
        if n_epochs_semisupervised is None:
            n_epochs_semisupervised = int(
                np.min([10, np.max([2, round(n_epochs_unsupervised / 3.0)])])
            )
        logger.info(
            "Training Unsupervised Trainer for {} epochs.".format(n_epochs_unsupervised)
        )
        logger.info(
            "Training SemiSupervised Trainer for {} epochs.".format(
                n_epochs_semisupervised
            )
        )

        if self._is_trained_base is not True:
            self._unsupervised_trainer = UnsupervisedTrainer(
                self._base_model,
                self.adata,
                train_size=train_size,
                test_size=test_size,
                n_iter_kl_warmup=n_iter_kl_warmup,
                n_epochs_kl_warmup=n_epochs_kl_warmup,
                frequency=frequency,
                use_cuda=self.use_cuda,
                **unsupervised_trainer_kwargs,
            )
            self._unsupervised_trainer.train(
                n_epochs=n_epochs_unsupervised, lr=lr, **unsupervised_train_kwargs
            )
            self.unsupervised_history_ = self._unsupervised_trainer.history
            self._is_trained_base = True

        self.model.load_state_dict(self._base_model.state_dict(), strict=False)

        if "frequency" not in semisupervised_trainer_kwargs and frequency is not None:
            semisupervised_trainer_kwargs["frequency"] = frequency

        self.trainer = SemiSupervisedTrainer(
            self.model,
            self.adata,
            use_cuda=self.use_cuda,
            **semisupervised_trainer_kwargs,
        )
        self.trainer.unlabelled_set = self.trainer.create_scvi_dl(
            indices=self._unlabeled_indices
        )
        self.trainer.labelled_set = self.trainer.create_scvi_dl(
            indices=self._labeled_indices
        )
        self.semisupervised_history_ = self.trainer.history
        self.trainer.train(
            n_epochs=n_epochs_semisupervised,
            **semisupervised_train_kwargs,
        )

        self.is_trained_ = True