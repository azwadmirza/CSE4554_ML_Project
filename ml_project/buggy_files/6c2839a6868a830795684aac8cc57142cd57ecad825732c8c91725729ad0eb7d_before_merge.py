    def history(self):
        """Returns computed metrics during training."""
        if self.is_trained_ is False:
            return {}
        else:
            return {
                "unsupervised_trainer_history": self._unsupervised_trainer.history,
                "semisupervised_trainer_history": self.trainer.history,
            }