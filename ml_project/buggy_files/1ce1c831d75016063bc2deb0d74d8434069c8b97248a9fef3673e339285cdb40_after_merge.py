    def restore(self, checkpoint_path):
        """Restores training state from a given model checkpoint.

        These checkpoints are returned from calls to save().
        """

        self._restore(checkpoint_path)
        metadata = pickle.load(open(checkpoint_path + ".rllib_metadata", "rb"))
        self.experiment_id = metadata[0]
        self.iteration = metadata[1]
        self.timesteps_total = metadata[2]
        self.time_total = metadata[3]