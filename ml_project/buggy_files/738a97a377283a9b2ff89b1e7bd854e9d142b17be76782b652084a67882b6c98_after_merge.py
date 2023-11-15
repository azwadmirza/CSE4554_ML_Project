    def _try_log_hparams(self, result):
        # TBX currently errors if the hparams value is None.
        flat_params = flatten_dict(self.trial.evaluated_params)
        scrubbed_params = {
            k: v
            for k, v in flat_params.items() if v is not None
        }
        from tensorboardX.summary import hparams
        experiment_tag, session_start_tag, session_end_tag = hparams(
            hparam_dict=scrubbed_params, metric_dict=result)
        self._file_writer.file_writer.add_summary(experiment_tag)
        self._file_writer.file_writer.add_summary(session_start_tag)
        self._file_writer.file_writer.add_summary(session_end_tag)