def lr_find(
        trainer,
        model: LightningModule,
        train_dataloader: Optional[DataLoader] = None,
        val_dataloaders: Optional[Union[DataLoader, List[DataLoader]]] = None,
        min_lr: float = 1e-8,
        max_lr: float = 1,
        num_training: int = 100,
        mode: str = 'exponential',
        early_stop_threshold: float = 4.0,
        datamodule: Optional[LightningDataModule] = None,
):
    r"""
    lr_find enables the user to do a range test of good initial learning rates,
    to reduce the amount of guesswork in picking a good starting learning rate.

    Args:
        model: Model to do range testing for

        train_dataloader: A PyTorch
            DataLoader with training samples. If the model has
            a predefined train_dataloader method, this will be skipped.

        min_lr: minimum learning rate to investigate

        max_lr: maximum learning rate to investigate

        num_training: number of learning rates to test

        mode: search strategy, either 'linear' or 'exponential'. If set to
            'linear' the learning rate will be searched by linearly increasing
            after each batch. If set to 'exponential', will increase learning
            rate exponentially.

        early_stop_threshold: threshold for stopping the search. If the
            loss at any point is larger than early_stop_threshold*best_loss
            then the search is stopped. To disable, set to None.

        datamodule: An optional `LightningDataModule` which holds the training
            and validation dataloader(s). Note that the `train_dataloader` and
            `val_dataloaders` parameters cannot be used at the same time as
            this parameter, or a `MisconfigurationException` will be raised.


    Example::

        # Setup model and trainer
        model = MyModelClass(hparams)
        trainer = pl.Trainer()

        # Run lr finder
        lr_finder = trainer.lr_find(model, ...)

        # Inspect results
        fig = lr_finder.plot(); fig.show()
        suggested_lr = lr_finder.suggestion()

        # Overwrite lr and create new model
        hparams.lr = suggested_lr
        model = MyModelClass(hparams)

        # Ready to train with new learning rate
        trainer.fit(model)

    """
    save_path = os.path.join(trainer.default_root_dir, 'lr_find_temp.ckpt')

    __lr_finder_dump_params(trainer, model)

    # Prevent going into infinite loop
    trainer.auto_lr_find = False

    # Initialize lr finder object (stores results)
    lr_finder = _LRFinder(mode, min_lr, max_lr, num_training)

    # Use special lr logger callback
    trainer.callbacks = [_LRCallback(num_training,
                                     early_stop_threshold,
                                     progress_bar_refresh_rate=1)]

    # No logging
    trainer.logger = DummyLogger()

    # Max step set to number of iterations
    trainer.max_steps = num_training

    # Disable standard progress bar for fit
    if trainer.progress_bar_callback:
        trainer.progress_bar_callback.disable()

    # Disable standard checkpoint & early stopping
    trainer.checkpoint_callback = False
    trainer.early_stop_callback = None

    # Required for saving the model
    trainer.optimizers, trainer.schedulers = [], [],
    trainer.model = model

    # Dump model checkpoint
    trainer.save_checkpoint(str(save_path))

    # Configure optimizer and scheduler
    optimizers, _, _ = trainer.init_optimizers(model)

    if len(optimizers) != 1:
        raise MisconfigurationException(
            f'`model.configure_optimizers()` returned {len(optimizers)}, but'
            ' learning rate finder only works with single optimizer')
    model.configure_optimizers = lr_finder._get_new_optimizer(optimizers[0])

    # Fit, lr & loss logged in callback
    trainer.fit(model,
                train_dataloader=train_dataloader,
                val_dataloaders=val_dataloaders,
                datamodule=datamodule)

    # Prompt if we stopped early
    if trainer.global_step != num_training:
        log.info('LR finder stopped early due to diverging loss.')

    # Transfer results from callback to lr finder object
    lr_finder.results.update({'lr': trainer.callbacks[0].lrs,
                              'loss': trainer.callbacks[0].losses})
    lr_finder._total_batch_idx = trainer.total_batch_idx  # for debug purpose

    # Reset model state
    trainer.checkpoint_connector.restore(str(save_path), on_gpu=trainer.on_gpu)
    os.remove(save_path)

    # Finish by resetting variables so trainer is ready to fit model
    __lr_finder_restore_params(trainer, model)
    if trainer.progress_bar_callback:
        trainer.progress_bar_callback.enable()

    return lr_finder