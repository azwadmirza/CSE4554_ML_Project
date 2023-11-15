    def training_step_and_backward(self, split_batch, batch_idx, opt_idx, optimizer, hiddens):
        """
        wrap the forward step in a closure so second order methods work
        """
        # lightning module hook
        result = self.training_step(split_batch, batch_idx, opt_idx, hiddens)

        if result is None:
            self.warning_cache.warn('training_step returned None if it was on purpose, ignore this warning...')
            return None

        # backward pass
        self.backward(result, optimizer, opt_idx)

        # hook
        self.on_after_backward(result.training_step_output, batch_idx, result.loss)

        return result