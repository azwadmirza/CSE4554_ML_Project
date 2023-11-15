    def optimizer_closure(self, split_batch, batch_idx, opt_idx, optimizer, hiddens):
        """
        wrap the forward step in a closure so second order methods work
        """
        # ---------------------------
        # FORWARD
        # ---------------------------
        with self.profiler.profile('model_forward'):
            if self.use_amp and NATIVE_AMP_AVALAIBLE:
                with torch.cuda.amp.autocast():
                    training_step_output = self.training_forward(split_batch, batch_idx,
                                                                 opt_idx, hiddens)
            else:
                training_step_output = self.training_forward(split_batch, batch_idx, opt_idx,
                                                             hiddens)

            # ----------------------------
            # PROCESS THE RESULT
            # ----------------------------
            # format and reduce outputs accordingly
            training_step_output_for_epoch_end = training_step_output
            training_step_output = self.process_output(training_step_output, train=True)

            # TODO: temporary part of structured results PR
            training_step_output = AttributeDict(
                batch_loss=training_step_output[0],
                pbar_on_batch_end=training_step_output[1],
                log_metrics=training_step_output[2],
                callback_metrics=training_step_output[3],
                hiddens=training_step_output[4],
            )

            # if the user decides to finally reduce things in epoch_end, save raw output without graphs
            training_step_output_for_epoch_end = recursive_detach(training_step_output_for_epoch_end)

        # accumulate loss
        # (if accumulate_grad_batches = 1 no effect)
        closure_loss = training_step_output.batch_loss / self.accumulate_grad_batches

        # backward pass
        model_ref = self.get_model()
        with self.profiler.profile('model_backward'):
            # scale loss for 16 bit
            if self.precision == 16 and not self.on_tpu:
                closure_loss = model_ref.amp_scale_loss(closure_loss, optimizer, opt_idx)

            # do backward pass
            model_ref.backward(self, closure_loss, optimizer, opt_idx)

            # once backward has been applied, release graph
            closure_loss = closure_loss.detach()
            training_step_output.batch_loss = training_step_output.batch_loss.detach()

        if self.use_horovod:
            # Synchronize Horovod to ensure gradient manipulations (e.g., loss scaling) are valid
            optimizer.synchronize()

        # insert after step hook
        if self.is_function_implemented('on_after_backward'):
            model_ref = self.get_model()
            with self.profiler.profile('on_after_backward'):
                model_ref.on_after_backward()

        result = AttributeDict(
            loss=closure_loss,
            training_step_output=training_step_output,
            training_step_output_for_epoch_end=training_step_output_for_epoch_end,
            hiddens=training_step_output.hiddens,
        )
        return result