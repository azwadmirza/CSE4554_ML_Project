    def save(self):
        """Saves the current model state to a checkpoint.

        Returns:
            Checkpoint path that may be passed to restore().
        """

        checkpoint_path = self._save()
        pickle.dump(
            [self.experiment_id, self.iteration, self.timesteps_total,
             self.time_total],
            open(checkpoint_path + ".rllib_metadata", "wb"))
        return checkpoint_path