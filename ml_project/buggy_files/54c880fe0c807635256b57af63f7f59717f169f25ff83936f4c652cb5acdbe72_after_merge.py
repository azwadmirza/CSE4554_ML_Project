    def run_training_epoch(self):

        # get model
        model = self.get_model()

        # Epoch start events
        self.run_on_epoch_start_hook(model)

        # modify dataloader if needed (ddp, etc...)
        train_dataloader = self.prepare_train_loop_dataloader(self.train_dataloader)

        # bookkeeping
        epoch_output = []
        should_check_val = False

        # structured result accumulators for callbacks
        early_stopping_accumulator = Accumulator()
        checkpoint_accumulator = Accumulator()

        # run epoch
        for batch_idx, (batch, is_last_batch) in self.profiler.profile_iterable(
                enumerate(_with_is_last(train_dataloader)), "get_train_batch"
        ):
            # stop epoch if we limited the number of training batches
            if batch_idx >= self.num_training_batches:
                break

            self.batch_idx = batch_idx
            model.global_step = self.global_step

            # ------------------------------------
            # TRAINING_STEP + TRAINING_STEP_END
            # ------------------------------------
            batch_output = self.run_training_batch(batch, batch_idx)

            # only track outputs when user implements training_epoch_end
            # otherwise we will build up unnecessary memory
            step_out = batch_output.training_step_output_for_epoch_end
            should_auto_reduce_train_result = isinstance(step_out, Result) and step_out.should_reduce_on_epoch_end
            if isinstance(step_out, dict) and 'early_stop_on' in step_out:
                early_stopping_accumulator.accumulate(step_out['early_stop_on'])

            if isinstance(step_out, dict) and 'checkpoint_on' in step_out:
                checkpoint_accumulator.accumulate(step_out['checkpoint_on'])

            if self.is_overridden('training_epoch_end', model=self.get_model()) or should_auto_reduce_train_result:
                epoch_output.append(batch_output.training_step_output_for_epoch_end)

            # update LR schedulers
            self.update_train_loop_lr_schedulers()

            # when returning -1 from train_step, we end epoch early
            self.should_stop = batch_output.signal == -1

            # -----------------------------------------
            # VALIDATE IF NEEDED + CHECKPOINT CALLBACK
            # -----------------------------------------
            should_check_val = self.should_check_val(batch_idx, is_last_batch)
            if should_check_val:
                self.run_evaluation(test_mode=False)

            # -----------------------------------------
            # SAVE LOGGERS (ie: Tensorboard, etc...)
            # -----------------------------------------
            self.save_loggers_in_training_loop(batch_idx)

            # -----------------------------------------
            # SAVE METRICS TO LOGGERS
            # -----------------------------------------
            self.save_train_loop_metrics_to_loggers(batch_idx, batch_output)

            # progress global step according to grads progress
            self.increment_accumulated_grad_global_step()

            # max steps reached, end training
            if self.max_steps is not None and self.max_steps == self.global_step:
                break

            # end epoch early
            # stop when the flag is changed or we've gone past the amount
            # requested in the batches
            if self.should_stop:
                break

        # let ddp devices catch up when using horovod
        self.sync_horovod()

        # process epoch outputs
        self.run_training_epoch_end(epoch_output, checkpoint_accumulator, early_stopping_accumulator)

        # checkpoint callback
        self.check_checkpoint_callback(should_check_val)

        # epoch end hook
        self.run_on_epoch_end_hook(model)