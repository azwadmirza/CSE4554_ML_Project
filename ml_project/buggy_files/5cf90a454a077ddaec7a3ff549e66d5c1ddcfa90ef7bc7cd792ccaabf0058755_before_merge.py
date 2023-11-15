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
                if self.use_amp and NATIVE_AMP_AVALAIBLE:
                    with torch.cuda.amp.autocast():
                        output = self.evaluation_forward(model, batch, batch_idx, dataloader_idx, test_mode)
                else:
                    output = self.evaluation_forward(model, batch, batch_idx, dataloader_idx, test_mode)

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
                dl_outputs.append(output)

            outputs.append(dl_outputs)

        eval_results = {}

        # with a single dataloader don't pass an array
        if len(dataloaders) == 1:
            outputs = outputs[0]

        # give model a chance to do something with the outputs (and method defined)
        if isinstance(model, (LightningDistributedDataParallel, LightningDataParallel)):
            model = model.module

        if test_mode:
            if self.is_overridden('test_end', model=model):
                # TODO: remove in v1.0.0
                eval_results = model.test_end(outputs)
                rank_zero_warn('Method `test_end` was deprecated in v0.7 and will be removed in v1.0.'
                               ' Use `test_epoch_end` instead.', DeprecationWarning)

            elif self.is_overridden('test_epoch_end', model=model):
                eval_results = model.test_epoch_end(outputs)

        else:
            if self.is_overridden('validation_end', model=model):
                # TODO: remove in v1.0.0
                eval_results = model.validation_end(outputs)
                rank_zero_warn('Method `validation_end` was deprecated in v0.7 and will be removed in v1.0.'
                               ' Use `validation_epoch_end` instead.', DeprecationWarning)

            elif self.is_overridden('validation_epoch_end', model=model):
                eval_results = model.validation_epoch_end(outputs)

        # enable train mode again
        model.train()

        # enable gradients to save memory
        torch.set_grad_enabled(True)

        return eval_results