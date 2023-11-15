    def check_checkpoint_callback(self, should_check_val):
        # when no val loop is present or fast-dev-run still need to call checkpoints
        # TODO bake this logic into the checkpoint callback
        should_activate = not self.is_overridden('validation_step') and not should_check_val
        if should_activate:
            checkpoint_callbacks = [c for c in self.callbacks if isinstance(c, ModelCheckpoint)]
            [c.on_validation_end(self, self.get_model()) for c in checkpoint_callbacks]