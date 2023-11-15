    def history(self):
        """Returns computed metrics during training."""
        return {
            "unsupervised_trainer_history": self.unsupervised_history_,
            "semisupervised_trainer_history": self.semisupervised_history_,
        }