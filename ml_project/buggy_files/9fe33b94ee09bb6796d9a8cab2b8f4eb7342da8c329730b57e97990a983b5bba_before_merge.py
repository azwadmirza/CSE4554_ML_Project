    def run_training_batch(self, batch, batch_idx, dataloader_idx):
        # track grad norms
        grad_norm_dic = {}

        # track all metrics for callbacks
        batch_callback_metrics = []

        # track metrics to log
        batch_log_metrics = []

        # bookkeeping
        using_results_obj = False
        self.trainer.hiddens = None

        # track all outputs across time and num of optimizers
        batch_outputs = [[] for _ in range(len(self.get_optimizers_iterable()))]

        if batch is None:
            return AttributeDict(signal=0, grad_norm_dic=grad_norm_dic)

        # hook
        response = self.trainer.call_hook('on_batch_start')
        if response == -1:
            return AttributeDict(signal=-1, grad_norm_dic=grad_norm_dic)

        # hook
        response = self.trainer.call_hook('on_train_batch_start', batch, batch_idx, dataloader_idx)
        if response == -1:
            return AttributeDict(signal=-1, grad_norm_dic=grad_norm_dic)

        # lightning module hook
        splits = self.tbptt_split_batch(batch)

        for split_idx, split_batch in enumerate(splits):
            self.trainer.split_idx = split_idx

            # loop over optimizers
            for opt_idx, optimizer in self.get_optimizers_iterable():
                # make sure only the gradients of the current optimizer's parameters are calculated
                # in the training step to prevent dangling gradients in multiple-optimizer setup.
                if len(self.trainer.optimizers) > 1:
                    for param in self.trainer.get_model().parameters():
                        param.requires_grad = False
                    for group in optimizer.param_groups:
                        for param in group['params']:
                            param.requires_grad = True

                # -------------------
                # calculate loss (train step + train step end)
                # -------------------
                opt_closure_result = self.training_step_and_backward(
                    split_batch,
                    batch_idx,
                    opt_idx,
                    optimizer,
                    self.trainer.hiddens
                )

                using_results_obj = isinstance(opt_closure_result.training_step_output, Result)

                # log metrics
                self.log_training_step_metrics(opt_closure_result, batch_callback_metrics, batch_log_metrics)

                # track hiddens
                self.trainer.hiddens = self.process_hiddens(opt_closure_result)

                # check if loss or model weights are nan
                if self.trainer.terminate_on_nan:
                    self.trainer.detect_nan_tensors(opt_closure_result.loss)

                # track total loss for logging (avoid mem leaks)
                self.accumulated_loss.append(opt_closure_result.loss)

                # track all the outputs across all steps
                batch_opt_idx = opt_idx if len(batch_outputs) > 1 else 0
                batch_outputs[batch_opt_idx].append(opt_closure_result.training_step_output_for_epoch_end)

                # ------------------------------
                # BACKWARD PASS
                # ------------------------------
                # gradient update with accumulated gradients
                accumulation_done = (self.trainer.batch_idx + 1) % self.trainer.accumulate_grad_batches == 0
                is_final_batch = (self.trainer.batch_idx + 1) == self.trainer.num_training_batches
                if accumulation_done or is_final_batch:
                    # hook
                    grad_norm_dic = self.on_before_backward(batch_idx, optimizer)

                    # wrap forward + backward pass in closure for 2nd order optimizers
                    train_step_and_backward_closure = lambda: self.training_step_and_backward(
                        split_batch, batch_idx, opt_idx, optimizer, self.trainer.hiddens,
                    ).loss

                    # optimizer step
                    self.optimizer_step(optimizer, opt_idx, batch_idx, train_step_and_backward_closure)

                    # hook
                    self.on_before_zero_grad(optimizer)

                    # clear gradients
                    self.optimizer_zero_grad(batch_idx, optimizer, opt_idx)

                    # calculate running loss for display
                    self.running_loss.append(
                        self.accumulated_loss.mean() * self.trainer.accumulate_grad_batches
                    )

                    # reset for next set of accumulated grads
                    self.accumulated_loss.reset()

        # collapse all metrics into one dict
        batch_log_metrics = {k: v for d in batch_log_metrics for k, v in d.items()}

        # track all metrics for callbacks
        self.trainer.logger_connector.callback_metrics.update(batch_log_metrics)
        self.trainer.logger_connector.callback_metrics.update(
            {k: v for d in batch_callback_metrics for k, v in d.items() if v is not None}
        )

        result = AttributeDict(
            signal=0,
            grad_norm_dic=grad_norm_dic,
            batch_log_metrics=batch_log_metrics,
            training_step_output_for_epoch_end=batch_outputs
        )
        return result