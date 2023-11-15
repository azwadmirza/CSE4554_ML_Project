    def train(self):
        # add signal handlers for process kills
        # def _signal_kill_handler(*args):
        #     return TrainerTrainLoopMixin.run_training_teardown(self)
        #
        # orig_signal_handlers = {}
        # for sig_name in SIGNAL_TERMINATE:
        #     orig_signal_handlers[sig_name] = signal.signal(getattr(signal, sig_name),
        #                                                    _signal_kill_handler)

        # get model
        model = self.get_model()

        # enable train mode
        model.train()

        # enable gradients
        torch.set_grad_enabled(True)

        # load data
        # if reload_dataloaders_every_epoch, this is moved to the epoch loop
        if not self.reload_dataloaders_every_epoch:
            self.reset_train_dataloader(model)

        if model.val_dataloader is not None:
            self.reset_val_dataloader(model)

        # Train start events
        with self.profiler.profile('on_train_start'):
            # callbacks
            self.on_train_start()
            # model hooks
            model.on_train_start()

        try:
            # run all epochs
            for epoch in range(self.current_epoch, self.max_epochs):
                # reset train dataloader
                if self.reload_dataloaders_every_epoch:
                    self.reset_train_dataloader(model)
                # set seed for distributed sampler (enables shuffling for each epoch)
                if (self.use_ddp or self.use_horovod) \
                        and hasattr(self.train_dataloader, 'sampler') \
                        and hasattr(self.train_dataloader.sampler, 'set_epoch'):
                    self.train_dataloader.sampler.set_epoch(epoch)

                # update training progress in trainer and model
                model.current_epoch = epoch
                self.current_epoch = epoch

                # changing gradient according accumulation_scheduler
                self.accumulation_scheduler.on_epoch_start(self, self.get_model())

                # stores accumulated grad fractions per batch
                self.batch_loss_value = TensorRunningAccum(
                    window_length=self.accumulate_grad_batches
                )

                # -----------------
                # RUN TNG EPOCH
                # -----------------
                self.run_training_epoch()

                if self.max_steps and self.max_steps <= self.global_step:
                    self.run_training_teardown()
                    return

                # update LR schedulers
                self.update_learning_rates(interval='epoch')

                # early stopping
                met_min_epochs = epoch >= self.min_epochs - 1
                met_min_steps = self.global_step >= self.min_steps if self.min_steps else True

                if self.should_stop:
                    if (met_min_epochs and met_min_steps) or self.fast_dev_run:
                        self.run_training_teardown()
                        return
                    else:
                        log.info('Trainer was signaled to stop but required minimum epochs'
                                 f' ({self.min_epochs}) or minimum steps ({self.min_steps}) has'
                                 ' not been met. Training will continue...')

            self.run_training_teardown()

        except KeyboardInterrupt:
            rank_zero_warn('Detected KeyboardInterrupt, attempting graceful shutdown...')

            # user could press ctrl+c many times... only shutdown once
            if not self.interrupted:
                self.interrupted = True
                self.on_keyboard_interrupt()

                self.run_training_teardown()