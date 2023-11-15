    def checkpoint(self, force=False):
        """Saves execution state to `self._local_checkpoint_dir`.

        Overwrites the current session checkpoint, which starts when self
        is instantiated. Throttle depends on self._checkpoint_period.

        Args:
            force (bool): Forces a checkpoint despite checkpoint_period.
        """
        if not self._local_checkpoint_dir:
            return
        now = time.time()
        if now - self._last_checkpoint_time < self._checkpoint_period and (
                not force):
            return
        self._last_checkpoint_time = now
        runner_state = {
            "checkpoints": list(
                self.trial_executor.get_checkpoints().values()),
            "runner_data": self.__getstate__(),
            "stats": {
                "start_time": self._start_time,
                "timestamp": self._last_checkpoint_time
            }
        }
        tmp_file_name = os.path.join(self._local_checkpoint_dir,
                                     ".tmp_checkpoint")
        with open(tmp_file_name, "w") as f:
            json.dump(runner_state, f, indent=2, cls=_TuneFunctionEncoder)

        os.replace(tmp_file_name, self.checkpoint_file)
        if force:
            self._syncer.sync_up()
        else:
            self._syncer.sync_up_if_needed()
        return self._local_checkpoint_dir