    def ddp_train(self, process_idx, model):
        """
        Entry point into a DP thread
        :param gpu_idx:
        :param model:
        :param cluster_obj:
        :return:
        """
        # node rank using relative slurm id if under slurm management
        # otherwise use given node rank or default to node rank 0
        try:
            node_id = os.environ['SLURM_NODEID'] if self.is_slurm_managing_tasks else os.environ['NODE_RANK']
            self.node_rank = int(node_id)
        except KeyError:
            log.warning("SLURM_NODEID or NODE_RANK environment variable is not defined. Set as 0.")
            self.node_rank = 0

        # show progressbar only on progress_rank 0
        self.progress_bar_refresh_rate = (
            self.progress_bar_refresh_rate if self.node_rank == 0 and process_idx == 0 else 0
        )

        # determine which process we are and world size
        if self.use_ddp:
            self.proc_rank = self.node_rank * self.num_processes + process_idx
            self.world_size = self.num_nodes * self.num_processes

        elif self.use_ddp2:
            self.proc_rank = self.node_rank
            self.world_size = self.num_nodes
        # set warning rank
        set_proc_rank(self.proc_rank)

        # let the exp know the rank to avoid overwriting logs
        if self.logger is not None:
            self.logger.rank = self.proc_rank

        # set up server using proc 0's ip address
        # try to init for 20 times at max in case ports are taken
        # where to store ip_table
        model.trainer = self
        model.init_ddp_connection(self.proc_rank, self.world_size, self.is_slurm_managing_tasks)

        # CHOOSE OPTIMIZER
        # allow for lr schedulers as well
        self.optimizers, self.lr_schedulers, self.optimizer_frequencies = self.init_optimizers(model)

        # MODEL
        # copy model to each gpu
        if self.on_gpu:
            self.root_gpu = process_idx
            torch.cuda.set_device(self.root_gpu)
            model.cuda(self.root_gpu)

        # set model properties before going into wrapper
        self.copy_trainer_model_properties(model)

        # AMP
        # run through amp wrapper before going to distributed DP
        if self.use_amp:
            # An example
            model, optimizers = model.configure_apex(amp, model, self.optimizers, self.amp_level)
            self.optimizers = optimizers

        # DDP2 uses all GPUs on the machine
        if self.distributed_backend == 'ddp':
            device_ids = [self.root_gpu]
        elif self.use_ddp2:
            device_ids = self.data_parallel_device_ids
        else:  # includes ddp_cpu
            device_ids = None

        # allow user to configure ddp
        model = model.configure_ddp(model, device_ids)

        # continue training routine
        self.run_pretrain_routine(model)

        # when ddp ends, we save the model
        self.save_spawn_weights(model)