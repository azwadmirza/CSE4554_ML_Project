    def horovod_train(self, model):
        # call setup after the ddp process has connected
        self.setup('fit')
        if self.is_function_implemented('setup', model):
            model.setup('fit')

        if torch.cuda.is_available() and self.on_gpu:
            # Horovod: pin GPU to local rank
            assert self.root_gpu == hvd.local_rank()
            torch.cuda.set_device(self.root_gpu)
            model.cuda(self.root_gpu)

        # avoid duplicating progress bar
        if hvd.rank() != 0 and self.progress_bar_callback is not None:
            self.progress_bar_callback.disable()

        # CHOOSE OPTIMIZER
        # allow for lr schedulers as well
        self.optimizers, self.lr_schedulers, self.optimizer_frequencies = self.init_optimizers(model)

        # Horovod: scale the learning rate by the number of workers to account for
        # increased total batch size
        for optimizer in self.optimizers:
            for param_group in optimizer.param_groups:
                param_group['lr'] *= hvd.size()

        if self.use_amp:
            # An example
            model, optimizers = model.configure_apex(amp, model, self.optimizers, self.amp_level)
            self.optimizers = optimizers
            self.reinit_scheduler_properties(self.optimizers, self.lr_schedulers)

        # Horovod: broadcast parameters & optimizer state to ensure consistent initialization
        hvd.broadcast_parameters(model.state_dict(), root_rank=0)
        for optimizer in self.optimizers:
            hvd.broadcast_optimizer_state(optimizer, root_rank=0)

        def filter_named_parameters(model, optimizer):
            opt_params = set([p for group in optimizer.param_groups for p in group.get('params', [])])
            return [(name, p) for name, p in model.named_parameters() if p in opt_params]

        # Horovod: wrap optimizers to perform gradient aggregation via allreduce
        self.optimizers = [
            hvd.DistributedOptimizer(optimizer, named_parameters=filter_named_parameters(model, optimizer))
            for optimizer in self.optimizers
        ]

        # Update logger rank info from Horovod to avoid race conditions from  different ranks
        # creating directories / writing files in the same locations.
        self.global_rank = hvd.rank()
        rank_zero_only.rank = self.global_rank

        with ExitStack() as stack:
            for optimizer in self.optimizers:
                # Synchronization will be performed explicitly following backward()
                stack.enter_context(optimizer.skip_synchronize())

            self.run_pretrain_routine(model)

        # Make sure all workers have finished training before returning to the user
        hvd.join()