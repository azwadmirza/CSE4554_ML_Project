    def forward(self, *inputs, **kwargs):  # pragma: no-cover
        self._sync_params()
        fx_called: str = ''

        if self.device_ids:
            inputs, kwargs = self.scatter(inputs, kwargs, self.device_ids)
            if len(self.device_ids) == 1:
                # --------------
                # LIGHTNING MOD
                # --------------
                # normal
                # output = self.module(*inputs[0], **kwargs[0])
                # lightning
                if self.module.training:
                    output = self.module.training_step(*inputs[0], **kwargs[0])
                    fx_called = 'training_step'
                elif self.module.testing:
                    output = self.module.test_step(*inputs[0], **kwargs[0])
                    fx_called = 'test_step'
                else:
                    output = self.module.validation_step(*inputs[0], **kwargs[0])
                    fx_called = 'validation_step'
            else:
                outputs = self.parallel_apply(self._module_copies[:len(inputs)], inputs, kwargs)
                output = self.gather(outputs, self.output_device)
        else:
            # output = self.module(*inputs, **kwargs)
            # normal lightning (ddp_cpu)
            if self.module.training:
                output = self.module.training_step(*inputs, **kwargs)
            elif self.module.testing:
                output = self.module.test_step(*inputs, **kwargs)
            else:
                output = self.module.validation_step(*inputs, **kwargs)

        if torch.is_grad_enabled():
            # We'll return the output object verbatim since it is a freeform
            # object. We need to find any tensors in this object, though,
            # because we need to figure out which parameters were used during
            # this forward pass, to ensure we short circuit reduction for any
            # unused parameters. Only if `find_unused_parameters` is set.
            if self.find_unused_parameters:
                self.reducer.prepare_for_backward(list(_find_tensors(output)))
            else:
                self.reducer.prepare_for_backward([])

        if output is None:
            warn_missing_output(fx_called)

            m = f'{fx_called} returned None. Did you forget to re'
        return output