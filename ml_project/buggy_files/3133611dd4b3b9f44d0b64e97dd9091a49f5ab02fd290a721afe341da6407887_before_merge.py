    def _process_training_step_output(self, training_step_output, split_batch):
        training_step_output_for_epoch_end = training_step_output

        # -----------------------------------------
        # process result return (DEPRECATE in 1.0)
        # -----------------------------------------
        if isinstance(training_step_output, Result):
            training_step_output_for_epoch_end = self._process_result(training_step_output, split_batch)
            return training_step_output_for_epoch_end, training_step_output

        # -----------------------------------------
        # process hybrid (1.0)
        # -----------------------------------------
        # no need for these checks in 1.0.0
        # TODO: remove checks in 1.0.0
        is_tensor = isinstance(training_step_output_for_epoch_end, torch.Tensor)
        is_1_0_output = is_tensor or ('log' not in training_step_output and 'progress_bar' not in training_step_output)
        if is_1_0_output:
            return self._process_training_step_output_1_0(training_step_output, split_batch)

        # -----------------------------------------
        # process old dict (deprecate 1.0)
        # -----------------------------------------
        training_step_output = self.trainer.process_dict_result(training_step_output, train=True)

        training_step_output = AttributeDict(
            batch_loss=training_step_output[0],
            pbar_on_batch_end=training_step_output[1],
            log_metrics=training_step_output[2],
            callback_metrics=training_step_output[3],
            hiddens=training_step_output[4],
        )
        # if the user decides to finally reduce things in epoch_end, save raw output without graphs
        if isinstance(training_step_output_for_epoch_end, torch.Tensor):
            training_step_output_for_epoch_end = training_step_output_for_epoch_end.detach()
        else:
            training_step_output_for_epoch_end = recursive_detach(training_step_output_for_epoch_end)

        return training_step_output_for_epoch_end, training_step_output