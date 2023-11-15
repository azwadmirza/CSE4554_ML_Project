    def fit(
            self,
            model: LightningModule,
            train_dataloader: Optional[DataLoader] = None,
            val_dataloaders: Optional[DataLoader] = None
    ):
        r"""
        Runs the full optimization routine.

        Args:
            model: Model to fit.

            train_dataloader: A Pytorch
                DataLoader with training samples. If the model has
                a predefined train_dataloader method this will be skipped.

            val_dataloaders: Either a single
                Pytorch Dataloader or a list of them, specifying validation samples.
                If the model has a predefined val_dataloaders method this will be skipped

        Example::

            # Option 1,
            # Define the train_dataloader() and val_dataloader() fxs
            # in the lightningModule
            # RECOMMENDED FOR MOST RESEARCH AND APPLICATIONS TO MAINTAIN READABILITY
            trainer = Trainer()
            model = LightningModule()
            trainer.fit(model)

            # Option 2
            # in production cases we might want to pass different datasets to the same model
            # Recommended for PRODUCTION SYSTEMS
            train, val = DataLoader(...), DataLoader(...)
            trainer = Trainer()
            model = LightningModule()
            trainer.fit(model, train_dataloader=train, val_dataloader=val)

            # Option 1 & 2 can be mixed, for example the training set can be
            # defined as part of the model, and validation can then be feed to .fit()

        """
        # bind logger and other properties
        model.logger = self.logger
        self.copy_trainer_model_properties(model)

        # set up the passed in dataloaders (if needed)
        self.__attach_dataloaders(model, train_dataloader, val_dataloaders)

        # check that model is configured correctly
        self.check_model_configuration(model)

        # download the data and do whatever transforms we need
        # do before any spawn calls so that the model can assign properties
        # only on proc 0 because no spawn has happened yet
        model.prepare_data()

        # Run learning rate finder:
        if self.auto_lr_find:
            self._run_lr_finder_internally(model)

        # route to appropriate start method
        # when using multi-node or DDP within a node start each module in a separate process
        if self.use_ddp2:
            task = int(os.environ['SLURM_LOCALID'])
            self.ddp_train(task, model)

        elif self.use_ddp:
            if self.is_slurm_managing_tasks:
                task = int(os.environ['SLURM_LOCALID'])
                self.ddp_train(task, model)
            else:
                self.__set_random_port()
                # track for predict
                self.model = model
                # train
                mp.spawn(self.ddp_train, nprocs=self.num_processes, args=(model,))
                # load weights if not interrupted
                self.load_spawn_weights(model)
                self.model = model

        # 1 gpu or dp option triggers training using DP module
        # easier to avoid NCCL issues
        elif self.use_dp:
            self.dp_train(model)

        elif self.use_horovod:
            self.horovod_train(model)

        elif self.single_gpu:
            self.single_gpu_train(model)

        elif self.use_tpu:  # pragma: no-cover
            log.info(f'training on {self.num_tpu_cores} TPU cores')

            #  COLAB_GPU is an env var available by default in Colab environments.
            start_method = 'fork' if os.getenv('COLAB_GPU') else 'spawn'

            # track for predict
            self.model = model

            # train
            xmp.spawn(self.tpu_train, args=(model,), nprocs=self.num_tpu_cores, start_method=start_method)

            # load weights if not interrupted
            self.load_spawn_weights(model)
            self.model = model

        # ON CPU
        else:
            # run through amp wrapper
            if self.use_amp:
                raise MisconfigurationException('amp + cpu is not supported.  Please use a GPU option')

            # CHOOSE OPTIMIZER
            # allow for lr schedulers as well
            self.optimizers, self.lr_schedulers, self.optimizer_frequencies = self.init_optimizers(model)

            self.run_pretrain_routine(model)

        # return 1 when finished
        # used for testing or when we need to know that training succeeded
        return 1