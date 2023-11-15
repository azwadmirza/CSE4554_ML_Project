    def tpu_train(self, tpu_core_idx, model):
        # put model on tpu
        model.to(xm.xla_device())

        # get the appropriate tpu ranks
        self.tpu_local_core_rank = xm.get_local_ordinal()
        self.tpu_global_core_rank = xm.get_ordinal()

        # avoid duplicating progress bar
        self.show_progress_bar = self.show_progress_bar and self.tpu_global_core_rank == 0

        # track current tpu
        self.current_tpu_idx = tpu_core_idx
        self.proc_rank = self.tpu_local_core_rank

        # CHOOSE OPTIMIZER
        # allow for lr schedulers as well
        self.optimizers, self.lr_schedulers = self.init_optimizers(model.configure_optimizers())

        # init 16 bit for TPU
        if self.precision == 16:
            os.environ['XLA_USE_BF16'] = 1

        m = f'INIT TPU local core: {self.tpu_local_core_rank}, ' \
            f'global rank: {self.tpu_global_core_rank}'
        log.info(m)
        self.run_pretrain_routine(model)

        self.save_spawn_weights(model)