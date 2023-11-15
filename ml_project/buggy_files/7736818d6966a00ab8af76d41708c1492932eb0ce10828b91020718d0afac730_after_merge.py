    def ddp_train(self, process_idx, model, is_master=False, proc_offset=0):
        """
        Entry point into a DP thread
        :param gpu_idx:
        :param model:
        :param cluster_obj:
        :return:
        """
        # offset the process id if requested
        process_idx = process_idx + proc_offset

        # show progressbar only on progress_rank 0
        if (self.node_rank != 0 or process_idx != 0) and self.progress_bar_callback is not None:
            self.progress_bar_callback.disable()

        # determine which process we are and world size
        if self.use_ddp:
            self.local_rank = process_idx
            self.global_rank = self.node_rank * self.num_processes + process_idx
            self.world_size = self.num_nodes * self.num_processes

        elif self.use_ddp2:
            self.local_rank = self.node_rank
            self.global_rank = self.node_rank
            self.world_size = self.num_nodes

        # set warning rank
        rank_zero_only.rank = self.global_rank

        # set up server using proc 0's ip address
        # try to init for 20 times at max in case ports are taken
        # where to store ip_table
        model.trainer = self
        model.init_ddp_connection(self.global_rank, self.world_size, self.is_slurm_managing_tasks)

        # call setup after the ddp process has connected
        self.setup()
        if self.is_function_implemented('setup', model):
            model.setup()

        # on world_size=0 let everyone know training is starting
        if self.is_global_zero:
            log.info('-' * 100)
            log.info(f'distributed_backend={self.distributed_backend}')
            log.info(f'All DDP processes registered. Starting ddp with {self.world_size} processes')
            log.info('-' * 100)

        # CHOOSE OPTIMIZER
        # allow for lr schedulers as well
        self.optimizers, self.lr_schedulers, self.optimizer_frequencies = self.init_optimizers(model)

        # MODEL
        # copy model to each gpu
        if self.on_gpu:
            gpu_idx = process_idx
            if is_master:
                # source of truth is cuda for gpu idx
                gpus = os.environ['CUDA_VISIBLE_DEVICES'].split(',')
                gpu_idx = int(gpus[self.local_rank])

            self.root_gpu = gpu_idx
            torch.cuda.set_device(self.root_gpu)
            model.cuda(self.root_gpu)

        # set model properties before going into wrapper
        self.copy_trainer_model_properties(model)

        # AMP
        # run through amp wrapper before going to distributed DP
        # TODO: remove in v0.8.0
        if self.use_amp and not self.use_native_amp:
            model, optimizers = model.configure_apex(amp, model, self.optimizers, self.amp_level)
            self.optimizers = optimizers
            self.reinit_scheduler_properties(self.optimizers, self.lr_schedulers)

        # DDP2 uses all GPUs on the machine
        if self.distributed_backend == 'ddp' or self.distributed_backend == 'ddp_spawn':
            device_ids = [self.root_gpu]
        elif self.use_ddp2:
            device_ids = self.data_parallel_device_ids
        else:  # includes ddp_cpu
            device_ids = None

        # allow user to configure ddp
        model = model.configure_ddp(model, device_ids)

        # continue training routine
        self.run_pretrain_routine(model)