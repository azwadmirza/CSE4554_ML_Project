    def training_step(self, split_batch, batch_idx, opt_idx, hiddens):
        # give the PL module a result for logging
        model = self.trainer.get_model()
        model._results = Result()
        model._current_fx_name = 'training_step'

        with self.trainer.profiler.profile('model_forward'):
            args = self.build_train_args(split_batch, batch_idx, opt_idx, hiddens)
            training_step_output = self.trainer.accelerator_backend.training_step(args)
            training_step_output = self.trainer.call_hook('training_step_end', training_step_output)

            training_step_output_for_epoch_end, training_step_output = self._process_training_step_output(
                training_step_output,
                split_batch
            )
            is_result_obj = isinstance(training_step_output, Result)

            if training_step_output_for_epoch_end is None:
                return None

        # accumulate loss
        # (if accumulate_grad_batches = 1 no effect)
        if is_result_obj:
            closure_loss = training_step_output.minimize
        else:
            closure_loss = training_step_output.batch_loss

        closure_loss = closure_loss / self.trainer.accumulate_grad_batches

        # the loss will get scaled for amp. avoid any modifications to it
        untouched_loss = closure_loss.detach().clone()

        # result
        result = AttributeDict(
            closure_loss=closure_loss,
            loss=untouched_loss,
            training_step_output=training_step_output,
            training_step_output_for_epoch_end=training_step_output_for_epoch_end,
            hiddens=training_step_output.hiddens,
        )
        return result