    def dump_checkpoint(self, weights_only: bool = False) -> dict:
        """Creating model checkpoint.

        Args:
            weights_only: saving model weights only

        Return:
             structured dictionary
        """
        checkpoint = {
            'epoch': self.current_epoch + 1,
            'global_step': self.global_step + 1,
            'pytorch-lightning_version': pytorch_lightning.__version__,
        }

        if not weights_only:

            # TODO support more generic way for callbacks to persist a state_dict in a checkpoint
            checkpoint_callbacks = [c for c in self.callbacks if isinstance(c, ModelCheckpoint)]
            early_stopping_callbacks = [c for c in self.callbacks if isinstance(c, EarlyStopping)]

            if checkpoint_callbacks:
                # we add the official checkpoint callback to the end of the list
                # extra user provided callbacks will not be persisted yet
                checkpoint['checkpoint_callback_best_model_score'] = self.checkpoint_callback.best_model_score
                checkpoint['checkpoint_callback_best_model_path'] = self.checkpoint_callback.best_model_path

            if early_stopping_callbacks and checkpoint_callbacks:
                # we add the official early stopping callback to the end of the list
                # extra user provided callbacks will not be persisted yet
                checkpoint['early_stop_callback_state_dict'] = early_stopping_callbacks[-1].state_dict()

            # save optimizers
            optimizer_states = []
            for i, optimizer in enumerate(self.optimizers):
                optimizer_states.append(optimizer.state_dict())
            checkpoint['optimizer_states'] = optimizer_states

            # save lr schedulers
            lr_schedulers = []
            for scheduler in self.lr_schedulers:
                lr_schedulers.append(scheduler['scheduler'].state_dict())
            checkpoint['lr_schedulers'] = lr_schedulers

            # save native amp scaling
            if self.use_amp and NATIVE_AMP_AVALAIBLE and not self.use_tpu:
                checkpoint['native_amp_scaling_state'] = self.scaler.state_dict()

        # add the module_arguments and state_dict from the model
        model = self.get_model()

        checkpoint['state_dict'] = model.state_dict()

        if model.hparams:
            if hasattr(model, '_hparams_name'):
                checkpoint[LightningModule.CHECKPOINT_HYPER_PARAMS_NAME] = model._hparams_name
            # add arguments to the checkpoint
            checkpoint[LightningModule.CHECKPOINT_HYPER_PARAMS_KEY] = model.hparams
            if Container is not None:
                if isinstance(model.hparams, Container):
                    checkpoint[LightningModule.CHECKPOINT_HYPER_PARAMS_TYPE] = type(model.hparams)

        # give the model a chance to add a few things
        model.on_save_checkpoint(checkpoint)

        return checkpoint