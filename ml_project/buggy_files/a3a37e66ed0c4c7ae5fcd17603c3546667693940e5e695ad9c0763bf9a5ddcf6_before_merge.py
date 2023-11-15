    def dp_train(self, model):

        # CHOOSE OPTIMIZER
        # allow for lr schedulers as well
        self.optimizers, self.lr_schedulers, self.optimizer_frequencies = self.init_optimizers(model)

        model.cuda(self.root_gpu)

        # hack forward to do autocast for the user
        model_autocast_original_forward = model.forward
        if self.use_amp and self.use_native_amp:
            # wrap the user's forward in autocast and give it back at the end
            model.forward = torch.cuda.amp.autocast()(model.forward)

        # TODO: remove in v0.8.0
        # check for this bug (amp + dp + !01 doesn't work)
        # https://github.com/NVIDIA/apex/issues/227
        if self.use_dp and self.use_amp and not self.use_native_amp:
            if self.amp_level == 'O2':
                raise MisconfigurationException(
                    f'Amp level {self.amp_level} with DataParallel is not supported.'
                    f' See this note from NVIDIA for more info: https://github.com/NVIDIA/apex/issues/227.'
                    f' We recommend you switch to ddp if you want to use amp')
            else:
                model, optimizers = model.configure_apex(amp, model, self.optimizers, self.amp_level)
                self.reinit_scheduler_properties(optimizers, self.lr_schedulers)

        # create list of device ids
        device_ids = self.data_parallel_device_ids
        if isinstance(device_ids, int):
            device_ids = list(range(device_ids))

        # set dp device
        torch.cuda.set_device(self.root_gpu)

        model = LightningDataParallel(model, device_ids=device_ids)

        self.run_pretrain_routine(model)

        model.forward = model_autocast_original_forward