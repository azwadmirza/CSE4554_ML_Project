    def train(
        self,
        n_epochs: Optional[int] = 200,
        kappa: Optional[int] = 5,
        discriminator: Optional[Classifier] = None,
        train_size: float = 0.9,
        frequency: int = 1,
        n_epochs_kl_warmup: int = 400,
        train_fun_kwargs: dict = {},
        **kwargs,
    ):
        """
        Train the model.

        Parameters
        ----------
        n_epochs
            Number of passes through the dataset.
        kappa
            Scaling parameter for the discriminator loss.
        discriminator
            :class:`~scvi.core.modules.Classifier` object.
        train_size
            Size of training set in the range [0.0, 1.0].
        frequency
            Frequency with which metrics are computed on the data for train/test/val sets.
        n_epochs_kl_warmup
            Number of passes through dataset for scaling term on KL divergence to go from 0 to 1.
        train_fun_kwargs
            Keyword args for the train method of :class:`~scvi.core.trainers.trainer.Trainer`.
        **kwargs
            Other keyword args for :class:`~scvi.core.trainers.trainer.Trainer`.
        """
        train_fun_kwargs = dict(train_fun_kwargs)
        if discriminator is None:
            discriminator = Classifier(self.model.n_latent, 32, 2, 3, logits=True)
        self.trainer = JVAETrainer(
            self.model,
            discriminator,
            self.adatas,
            train_size,
            frequency=frequency,
            kappa=kappa,
            n_epochs_kl_warmup=n_epochs_kl_warmup,
        )

        logger.info("Training for {} epochs.".format(n_epochs))
        self.trainer.train(n_epochs=n_epochs, **train_fun_kwargs)

        self.is_trained_ = True