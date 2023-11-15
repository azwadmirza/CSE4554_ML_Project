    def tpu_train(self, tpu_core_idx, model):
        # call setup after the ddp process has connected
        self.setup('fit')
        if self.is_function_implemented('setup', model):
            model.setup('fit')

        # put model on tpu
        self._device = xm.xla_device(self.tpu_id) if self.tpu_id is not None else xm.xla_device()
        model.to(self._device)

        # get the appropriate tpu ranks
        self.tpu_local_core_rank = xm.get_local_ordinal()
        self.tpu_global_core_rank = xm.get_ordinal()

        # avoid duplicating progress bar
        if self.tpu_global_core_rank != 0 and self.progress_bar_callback is not None:
            self.progress_bar_callback.disable()

        self.global_rank = self.tpu_local_core_rank
        rank_zero_only.rank = self.global_rank

        # CHOOSE OPTIMIZER
        # allow for lr schedulers as well
        self.optimizers, self.lr_schedulers, self.optimizer_frequencies = self.init_optimizers(model)

        # init 16 bit for TPU
        if self.precision == 16:
            os.environ['XLA_USE_BF16'] = str(1)

        log.info(f'INIT TPU local core: {self.tpu_local_core_rank},'
                 f' global rank: {self.tpu_global_core_rank}')

        # continue training routine
        self.run_pretrain_routine(model)

        # when training ends on these platforms dump weights to get out of the main process
        if self.on_colab_kaggle:
            self.save_spawn_weights(model)