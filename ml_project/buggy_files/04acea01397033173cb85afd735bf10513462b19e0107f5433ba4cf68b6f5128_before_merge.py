    def log_train_epoch_end_metrics(self,
                                    epoch_output,
                                    checkpoint_accumulator,
                                    early_stopping_accumulator,
                                    num_optimizers):
        # epoch output is a list. Each item in that list has all the outputs per optimizer
        # epoch_output[optimizer_idx][training_step_idx][tbptt_index]
        # remember that not using truncated backprop is equivalent with truncated back prop of len(1)

        model = self.trainer.get_model()

        epoch_callback_metrics = {}

        # -----------------------
        # Calculate epoch callback values if given
        # -----------------------
        if checkpoint_accumulator.num_values > 0:
            epoch_callback_metrics['checkpoint_on'] = checkpoint_accumulator.mean()

        if early_stopping_accumulator.num_values > 0:
            epoch_callback_metrics['early_stop_on'] = early_stopping_accumulator.mean()

        # ------------------------
        # determine if using a result obj
        # ------------------------
        # [optimizer_idx][training_step_idx][tbptt_index]
        opt_idx_outputs = epoch_output[0]

        # TODO: deprecate 1.0
        try:
            sample_obj = opt_idx_outputs[0][0] if isinstance(opt_idx_outputs[0], list) else opt_idx_outputs[0]
            is_result_obj = len(epoch_output) > 0 and isinstance(sample_obj, Result)
            is_1_0_result = is_result_obj and 'extra' in sample_obj
        except IndexError as e:
            is_result_obj = False
            is_1_0_result = False

        # ------------------
        # NEW 1.0.0 PATH
        # ------------------
        if is_1_0_result:
            # lightning module hook
            self.training_epoch_end(model, epoch_output, num_optimizers)

            # log/aggregate metrics automatically
            epoch_log_metrics, epoch_progress_bar_metrics = self.__auto_reduce_results_on_epoch_end(epoch_output)

        # TODO: deprecate 1.0
        else:
            out = self.__run_legacy_training_epoch_end(
                num_optimizers,
                epoch_output,
                model,
                is_result_obj,
                epoch_callback_metrics
            )
            epoch_log_metrics, epoch_progress_bar_metrics, epoch_callback_metrics = out

        # it will perform reduction over epoch and return log metrics
        cached_epoch_log_metrics = self.cached_results.get_epoch_log_metrics()
        cached_epoch_pbar_metrics = self.cached_results.get_epoch_pbar_metrics()

        # update
        epoch_log_metrics.update(cached_epoch_log_metrics)
        epoch_progress_bar_metrics.update(cached_epoch_pbar_metrics)

        # --------------------------
        # track results
        # --------------------------
        # add the metrics to the loggers and callbacks
        if epoch_log_metrics and len(epoch_log_metrics) > 0:
            self.log_metrics(epoch_log_metrics, {})
            self.callback_metrics.update(epoch_log_metrics)

        # add metrics to callbacks
        self.callback_metrics.update(epoch_callback_metrics)

        # add metrics to progress_bar and callbacks
        if len(epoch_progress_bar_metrics) > 0:
            self.add_progress_bar_metrics(epoch_progress_bar_metrics)
            self.callback_metrics.update(epoch_progress_bar_metrics)

        # reset epoch loop result for next epoch
        self.cached_results.reset()