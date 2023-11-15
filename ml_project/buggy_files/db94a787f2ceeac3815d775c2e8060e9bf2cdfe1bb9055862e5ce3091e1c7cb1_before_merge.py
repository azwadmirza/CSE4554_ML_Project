    def close(self):
        if self._file_writer is not None:
            if self.trial and self.trial.evaluated_params and self.last_result:
                scrubbed_result = {
                    k: value
                    for k, value in self.last_result.items()
                    if type(value) in VALID_SUMMARY_TYPES
                }
                self._try_log_hparams(scrubbed_result)
            self._file_writer.close()