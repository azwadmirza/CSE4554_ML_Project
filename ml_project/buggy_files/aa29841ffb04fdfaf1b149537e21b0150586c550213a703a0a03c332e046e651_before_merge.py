    def on_trial_complete(self, iteration: int, trials: List["Trial"],
                          trial: "Trial", **info):
        trial_syncer = self._get_trial_syncer(trial)
        if NODE_IP in trial.last_result:
            trainable_ip = trial.last_result[NODE_IP]
        else:
            trainable_ip = ray.get(trial.runner.get_current_ip.remote())
        trial_syncer.set_worker_ip(trainable_ip)
        trial_syncer.sync_down_if_needed()