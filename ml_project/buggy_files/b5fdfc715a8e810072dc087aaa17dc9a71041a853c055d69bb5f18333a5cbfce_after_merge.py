    def fit(
            self,
            model: LightningModule,
            train_dataloader: Optional[DataLoader] = None,
            val_dataloaders: Optional[Union[DataLoader, List[DataLoader]]] = None
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
            trainer.fit(model, train_dataloader=train, val_dataloaders=val)

            # Option 1 & 2 can be mixed, for example the training set can be
            # defined as part of the model, and validation can then be feed to .fit()

        """
        # bind logger and other properties
        model.logger = self.logger
        self.copy_trainer_model_properties(model)

        # clean hparams
        if hasattr(model, 'hparams'):
            parsing.clean_namespace(model.hparams)

        # set up the passed in dataloaders (if needed)
        self.__attach_dataloaders(model, train_dataloader, val_dataloaders)

        # check that model is configured correctly
        self.check_model_configuration(model)

        # callbacks
        self.on_fit_start()
        if self.is_function_implemented('on_fit_start', model):
            model.on_fit_start()

        # on multi-gpu jobs we only want to manipulate (download, etc) on node_rank=0, local_rank=0
        # or in the case where each node needs to do its own manipulation in which case just local_rank=0
        if self.can_prepare_data():
            model.prepare_data()
            self._is_data_prepared = True

        # Run auto batch size scaling
        if self.auto_scale_batch_size:
            if isinstance(self.auto_scale_batch_size, bool):
                self.auto_scale_batch_size = 'power'
            self.scale_batch_size(model, mode=self.auto_scale_batch_size)
            model.logger = self.logger  # reset logger binding

        # Run learning rate finder:
        if self.auto_lr_find:
            self._run_lr_finder_internally(model)
            model.logger = self.logger  # reset logger binding

        # route to appropriate start method
        # when using multi-node or DDP within a node start each module in a separate process
        if self.use_ddp2:
            if self.is_slurm_managing_tasks:
                task = int(os.environ['SLURM_LOCALID'])

            # torchelastic or general non_slurm ddp2
            elif 'WORLD_SIZE' in os.environ and ('GROUP_RANK' in os.environ or 'NODE_RANK' in os.environ):
                task = int(os.environ['LOCAL_RANK'])

            self.ddp_train(task, model)
        elif self.use_ddp:
            if self.is_slurm_managing_tasks:
                task = int(os.environ['SLURM_LOCALID'])
                self.ddp_train(task, model)

            # torchelastic or general non_slurm ddp
            elif 'WORLD_SIZE' in os.environ and ('GROUP_RANK' in os.environ or 'NODE_RANK' in os.environ):
                task = int(os.environ['LOCAL_RANK'])
                self.ddp_train(task, model)

            elif self.distributed_backend == 'cpu_ddp':
                self.set_random_port()
                self.model = model
                mp.spawn(self.ddp_train, nprocs=self.num_processes, args=(model,))

            elif self.distributed_backend == 'ddp_spawn':
                self.set_random_port()
                model.share_memory()

                # spin up peers
                mp.spawn(self.ddp_train, nprocs=self.num_processes, args=(model, ))

            elif self.distributed_backend == 'ddp':
                self.set_random_port()
                self.spawn_ddp_children(model)

        # 1 gpu or dp option triggers training using DP module
        # easier to avoid NCCL issues
        elif self.use_dp:
            self.dp_train(model)

        elif self.use_horovod:
            self.horovod_train(model)

        elif self.single_gpu:
            self.single_gpu_train(model)

        elif self.use_tpu:  # pragma: no-cover
            rank_zero_info(f'training on {self.tpu_cores} TPU cores')

            #  COLAB_GPU is an env var available by default in Colab environments.
            start_method = 'fork' if self.on_colab_kaggle else 'spawn'

            # track for predict
            self.model = model

            # wait for all prepare data nodes to finish
            self.barrier('setup')

            # train
            if self.tpu_id is not None:
                self.tpu_train(self.tpu_id, model)
            else:
                xmp.spawn(self.tpu_train, args=(model,), nprocs=self.tpu_cores, start_method=start_method)

            # load weights if not interrupted
            self.load_spawn_weights(model)
            self.model = model

        # ON CPU
        else:
            # run through amp wrapper
            if self.use_amp:
                raise MisconfigurationException('amp + cpu is not supported.  Please use a GPU option')

            # call setup after the ddp process has connected
            self.setup('fit')
            if self.is_function_implemented('setup', model):
                model.setup('fit')

            # CHOOSE OPTIMIZER
            # allow for lr schedulers as well
            self.optimizers, self.lr_schedulers, self.optimizer_frequencies = self.init_optimizers(model)

            self.run_pretrain_routine(model)

        # callbacks
        self.on_fit_end()

        # model hooks
        if self.is_function_implemented('on_fit_end'):
            model.on_fit_end()

        self.teardown('fit')
        if self.is_function_implemented('teardown'):
            model.teardown('fit')

        # return 1 when finished
        # used for testing or when we need to know that training succeeded
        return 1