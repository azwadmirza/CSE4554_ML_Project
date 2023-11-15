    def dp_train(self, model):
        # call setup after the ddp process has connected
        self.setup('fit')
        if self.is_function_implemented('setup', model):
            model.setup('fit')

        model.cuda(self.root_gpu)

        # CHOOSE OPTIMIZER
        # allow for lr schedulers as well
        self.optimizers, self.lr_schedulers, self.optimizer_frequencies = self.init_optimizers(model)

        # hack forward to do autocast for the user
        model_autocast_original_forward = model.forward
        if self.use_amp and NATIVE_AMP_AVALAIBLE and not self.use_tpu:
            # wrap the user's forward in autocast and give it back at the end
            model.forward = torch.cuda.amp.autocast()(model.forward)

        # TODO: remove with dropping NVIDIA AMP support
        # check for this bug (amp + dp + !01 doesn't work)
        # https://github.com/NVIDIA/apex/issues/227
        if self.use_dp and self.use_amp and not NATIVE_AMP_AVALAIBLE and not self.use_tpu:
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

        result = self.run_pretrain_routine(model)
        model.forward = model_autocast_original_forward

        return result