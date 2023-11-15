    def run_pretrain_routine(self, model: LightningModule):
        """Sanity check a few things before starting actual training.

        Args:
            model: The model to run sanity test on.
        """
        ref_model = model
        if self.data_parallel:
            ref_model = model.module

        # give model convenience properties
        ref_model.trainer = self

        # set local properties on the model
        self.copy_trainer_model_properties(ref_model)

        # init amp. Must be done here instead of __init__ to allow ddp to work
        if NATIVE_AMP_AVALAIBLE and self.precision == 16 and not self.use_tpu:
            self.scaler = torch.cuda.amp.GradScaler()

        # log hyper-parameters
        if self.logger is not None:
            # save exp to get started
            self.logger.log_hyperparams(ref_model.hparams)

            self.logger.save()

        if self.use_ddp or self.use_ddp2:
            torch_distrib.barrier()

        # wait for all models to restore weights
        if self.on_tpu and XLA_AVAILABLE:
            # wait for all processes to catch up
            torch_xla.core.xla_model.rendezvous("pl.Trainer.run_pretrain_routine")

        elif self.use_horovod:
            # wait for all processes to catch up
            hvd.join()

        # register auto-resubmit when on SLURM
        self.register_slurm_signal_handlers()

        # print model summary
        if self.is_global_zero and self.weights_summary is not None and not self.testing:
            if self.weights_summary in ModelSummary.MODES:
                ref_model.summarize(mode=self.weights_summary)
            else:
                raise MisconfigurationException(
                    "weights_summary can be None, " + ", ".join(ModelSummary.MODES)
                )

        # track model now.
        # if cluster resets state, the model will update with the saved weights
        self.model = model

        # restore training and model before hpc is called
        self.restore_weights(model)

        # when testing requested only run test and return
        if self.testing:
            # only load test dataloader for testing
            # self.reset_test_dataloader(ref_model)
            results = self.run_evaluation(test_mode=True)

            # remove all cuda tensors
            if results is not None and isinstance(results, dict) and len(results) > 0:
                for k, v in results.items():
                    if isinstance(v, torch.Tensor):
                        results[k] = v.cpu().item()

                return results
            else:
                return 1

        # check if we should run validation during training
        self.disable_validation = not (self.is_overridden('validation_step') and self.limit_val_batches > 0) \
            and not self.fast_dev_run

        # run tiny validation (if validation defined)
        # to make sure program won't crash during val
        if not self.disable_validation and self.num_sanity_val_steps > 0:
            self.reset_val_dataloader(ref_model)

            # hook and callback
            ref_model.on_sanity_check_start()
            self.on_sanity_check_start()

            num_loaders = len(self.val_dataloaders)
            max_batches = [self.num_sanity_val_steps] * num_loaders
            eval_results = self._evaluate(model,
                                          self.val_dataloaders,
                                          max_batches,
                                          False)

            # allow no returns from eval
            if eval_results is not None and len(eval_results) > 0:
                _, _, _, callback_metrics, _ = self.process_output(eval_results)
                self.callback_metrics = callback_metrics

            self.on_sanity_check_end()

        # clear cache before training
        if self.on_gpu and self.root_gpu is not None:
            # use context because of:
            # https://discuss.pytorch.org/t/out-of-memory-when-i-use-torch-cuda-empty-cache/57898
            with torch.cuda.device(f'cuda:{self.root_gpu}'):
                torch.cuda.empty_cache()

        # CORE TRAINING LOOP
        self.train()