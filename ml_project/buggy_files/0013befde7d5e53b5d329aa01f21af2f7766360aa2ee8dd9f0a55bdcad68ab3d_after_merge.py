    def lr_find(self,
                model: LightningModule,
                train_dataloader: Optional[DataLoader] = None,
                val_dataloaders: Optional[DataLoader] = None,
                min_lr: float = 1e-8,
                max_lr: float = 1,
                num_training: int = 100,
                mode: str = 'exponential',
                num_accumulation_steps: int = 1):
        r"""
        lr_find enables the user to do a range test of good initial learning rates,
        to reduce the amount of guesswork in picking a good starting learning rate.

        Args:
            model: Model to do range testing for

            train_dataloader: A PyTorch
                DataLoader with training samples. If the model has
                a predefined train_dataloader method this will be skipped.

            min_lr: minimum learning rate to investigate

            max_lr: maximum learning rate to investigate

            num_training: number of learning rates to test

            mode: search strategy, either 'linear' or 'exponential'. If set to
                'linear' the learning rate will be searched by linearly increasing
                after each batch. If set to 'exponential', will increase learning
                rate exponentially.

            num_accumulation_steps: number of batches to calculate loss over.

        Example::

            # Setup model and trainer
            model = MyModelClass(hparams)
            trainer = pl.Trainer()

            # Run lr finder
            lr_finder = trainer.lr_find(model, ...)

            # Inspect results
            fig = lr_finder.plot(); fig.show()
            suggested_lr = lr_finder.suggest()

            # Overwrite lr and create new model
            hparams.lr = suggested_lr
            model = MyModelClass(hparams)

            # Ready to train with new learning rate
            trainer.fit(model)

        """
        save_path = os.path.join(self.default_root_dir, 'lr_find_temp.ckpt')

        self._lr_finder_dump_params(model)

        # Prevent going into infinite loop
        self.auto_lr_find = False

        # Initialize lr finder object (stores results)
        lr_finder = _LRFinder(mode, min_lr, max_lr, num_training)

        # Use special lr logger callback
        self.callbacks = [_LRCallback(num_training, progress_bar_refresh_rate=1)]

        # No logging
        self.logger = None

        # Max step set to number of iterations
        self.max_steps = num_training

        # Disable standard progress bar for fit
        if self.progress_bar_callback:
            self.progress_bar_callback.disable()

        # Accumulation of gradients
        self.accumulate_grad_batches = num_accumulation_steps

        # Disable standard checkpoint & early stopping
        self.checkpoint_callback = False
        self.early_stop_callback = None
        self.enable_early_stop = False

        # Required for saving the model
        self.optimizers, self.schedulers = [], [],
        self.model = model

        # Dump model checkpoint
        self.save_checkpoint(str(save_path))

        # Configure optimizer and scheduler
        optimizers, _, _ = self.init_optimizers(model)

        if len(optimizers) != 1:
            raise MisconfigurationException(
                f'`model.configure_optimizers()` returned {len(optimizers)}, but'
                ' learning rate finder only works with single optimizer')
        configure_optimizers = model.configure_optimizers
        model.configure_optimizers = lr_finder._get_new_optimizer(optimizers[0])

        # Fit, lr & loss logged in callback
        self.fit(model,
                 train_dataloader=train_dataloader,
                 val_dataloaders=val_dataloaders)

        # Prompt if we stopped early
        if self.global_step != num_training:
            log.info('LR finder stopped early due to diverging loss.')

        # Transfer results from callback to lr finder object
        lr_finder.results.update({'lr': self.callbacks[0].lrs,
                                  'loss': self.callbacks[0].losses})

        # Reset model state
        self.restore(str(save_path), on_gpu=self.on_gpu)
        os.remove(save_path)

        # Finish by resetting variables so trainer is ready to fit model
        self._lr_finder_restore_params(model)
        if self.progress_bar_callback:
            self.progress_bar_callback.enable()

        return lr_finder