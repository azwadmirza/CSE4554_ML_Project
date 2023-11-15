    def single_gpu_train(self, model):
        model.cuda(self.root_gpu)

        # CHOOSE OPTIMIZER
        # allow for lr schedulers as well
        self.optimizers, self.lr_schedulers, self.optimizer_frequencies = self.init_optimizers(model)

        # TODO: update for 0.8.0
        if self.use_amp and not self.use_native_amp:
            # An example
            model, optimizers = model.configure_apex(amp, model, self.optimizers, self.amp_level)
            self.optimizers = optimizers
            self.reinit_scheduler_properties(self.optimizers, self.lr_schedulers)

        self.run_pretrain_routine(model)