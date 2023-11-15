    def _evaluate(
        self,
        model: LightningModule,
        dataloaders: List[DataLoader],
        max_batches: Union[int, List[int]],
        test_mode: bool = False
    ):
        """Run evaluation code.

        Args:
            model: The model to evaluate.
            dataloaders: A list of PyTorch dataloaders.
            max_batches: An integer or list of integers with length of the number of dataloaders. Each
                entry is the number of batches to process in the corresponding dataloader.
            test_mode:
        """
        # enable eval mode
        model.zero_grad()
        model.eval()

        # copy properties for forward overrides
        self.copy_trainer_model_properties(model)

        # disable gradients to save memory
        torch.set_grad_enabled(False)

        # bookkeeping
        outputs = []

        # convert max_batches to list
        if isinstance(max_batches, int):
            max_batches = [max_batches] * len(dataloaders)

        # --------------------------
        # ON_EVAL_EPOCH_START hook
        # --------------------------
        self.__call_eval_loop_hook_start(test_mode)

        # run validation
        for dataloader_idx, dataloader in enumerate(dataloaders):
            dl_outputs = []

            # on TPU we have to wrap it under the ParallelLoader
            if self.use_tpu:
                device = xm.xla_device(self.tpu_id)
                dataloader = xla_pl.ParallelLoader(dataloader, [device])
                dataloader = dataloader.per_device_loader(device)

            # each dataloader has a max num batches
            dl_max_batches = max_batches[dataloader_idx]

            for batch_idx, batch in enumerate(dataloader):
                if batch is None:
                    continue

                # stop short when on fast_dev_run (sets max_batch=1)
                if batch_idx >= dl_max_batches:
                    break

                # callbacks
                if test_mode:
                    self.on_test_batch_start()
                else:
                    self.on_validation_batch_start()

                # -----------------
                # RUN EVALUATION STEP
                # -----------------
                if self.use_amp and NATIVE_AMP_AVALAIBLE and not self.use_tpu:
                    with torch.cuda.amp.autocast():
                        output = self.evaluation_forward(model, batch, batch_idx, dataloader_idx, test_mode)
                else:
                    output = self.evaluation_forward(model, batch, batch_idx, dataloader_idx, test_mode)

                # allow only EvalResult when using structured results (from val_step)
                if isinstance(output, Result) and not isinstance(output, EvalResult):
                    m = 'only EvalResults or dicts are allowed from validation_step'
                    raise MisconfigurationException(m)

                # on dp / ddp2 might still want to do something with the batch parts
                if test_mode:
                    if self.is_overridden('test_step_end'):
                        model_ref = self.get_model()
                        with self.profiler.profile('test_step_end'):
                            output = model_ref.test_step_end(output)
                    self.on_test_batch_end()
                else:
                    if self.is_overridden('validation_step_end'):
                        model_ref = self.get_model()
                        with self.profiler.profile('validation_step_end'):
                            output = model_ref.validation_step_end(output)
                    self.on_validation_batch_end()

                # track outputs for collation
                if output is not None:
                    dl_outputs.append(output)

                self.__eval_add_step_metrics(output)

            outputs.append(dl_outputs)

        # ---------------------
        # EVAL_EPOCH_END
        # ---------------------
        using_eval_result = len(outputs) > 0 and len(outputs[0]) > 0 and isinstance(outputs[0][0], EvalResult)
        eval_results = self.__run_eval_epoch_end(test_mode, outputs, dataloaders, using_eval_result)

        # log callback metrics
        self.__update_callback_metrics(eval_results, using_eval_result)

        # enable train mode again
        model.train()

        # enable gradients to save memory
        torch.set_grad_enabled(True)

        # --------------------------
        # ON_EVAL_EPOCH_END hook
        # --------------------------
        self.__call_eval_loop_hook_end(test_mode)

        return eval_results