    def run_training_teardown(self):
        if hasattr(self, '_teardown_already_run') and self._teardown_already_run:
            return
        # Train end events
        with self.profiler.profile('on_train_end'):
            # callbacks
            self.on_train_end()
            # model hooks
            if self.is_function_implemented('on_train_end'):
                self.get_model().on_train_end()

        if self.logger is not None:
            self.logger.finalize("success")

        # summarize profile results
        self.profiler.describe()
        self._teardown_already_run = True