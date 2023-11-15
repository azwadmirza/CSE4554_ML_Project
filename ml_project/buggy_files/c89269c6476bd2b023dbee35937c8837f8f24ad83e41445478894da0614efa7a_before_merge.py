    def reset_trial(self,
                    trial,
                    new_config,
                    new_experiment_tag,
                    logger_creator=None):
        """Tries to invoke `Trainable.reset()` to reset trial.

        Args:
            trial (Trial): Trial to be reset.
            new_config (dict): New configuration for Trial trainable.
            new_experiment_tag (str): New experiment name for trial.
            logger_creator (Callable[[Dict], Logger]): A function that
                instantiates a logger on the actor process.

        Returns:
            True if `reset_config` is successful else False.
        """
        trial.set_experiment_tag(new_experiment_tag)
        trial.set_config(new_config)
        trainable = trial.runner
        with self._change_working_directory(trial):
            with warn_if_slow("reset"):
                try:
                    reset_val = ray.get(
                        trainable.reset.remote(new_config, logger_creator),
                        timeout=DEFAULT_GET_TIMEOUT)
                except GetTimeoutError:
                    logger.exception("Trial %s: reset timed out.", trial)
                    return False
        return reset_val