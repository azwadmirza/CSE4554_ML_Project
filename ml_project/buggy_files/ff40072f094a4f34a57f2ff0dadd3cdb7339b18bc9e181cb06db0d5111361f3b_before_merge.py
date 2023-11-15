    def call_optimizer_step(self, optimizer, opt_idx, batch_idx, split_batch):
        # calls .step(), .zero_grad()
        # override function to modify this behavior
        model = self.get_model()

        with self.profiler.profile('optimizer_step'):
            lambda_closure = lambda: self.optimizer_closure(
                split_batch,
                batch_idx,
                opt_idx,
                optimizer,
                self.hiddens
            ).loss

            # apply TPU optimizer
            if self.use_tpu and XLA_AVAILABLE:
                model.optimizer_step(self.current_epoch, batch_idx,
                                     optimizer, opt_idx, lambda_closure, on_tpu=True)

            # for LBFGS do something a bit different
            elif isinstance(optimizer, torch.optim.LBFGS):

                # native amp + lbfgs is a no go right now
                if self.use_amp and NATIVE_AMP_AVALAIBLE:
                    raise MisconfigurationException(
                        'native PyTorch amp and lbfgs are not compatible.'
                        ' To request, please file a Github issue in PyTorch and tag @mcarilli')
                model.optimizer_step(self.current_epoch, batch_idx, optimizer, opt_idx, lambda_closure,
                                     using_lbfgs=True)

            # when using 16-bit
            else:
                native_amp = self.use_amp and NATIVE_AMP_AVALAIBLE
                model.optimizer_step(self.current_epoch, batch_idx, optimizer, opt_idx, lambda_closure,
                                     using_native_amp=native_amp)

            # in native 16-bit we need to update scaler after optimizer step
            if self.use_amp and NATIVE_AMP_AVALAIBLE:
                self.scaler.update()

            # model hook
            model.on_before_zero_grad(optimizer)

            # clear gradients
            model.optimizer_zero_grad(self.current_epoch, batch_idx, optimizer, opt_idx)