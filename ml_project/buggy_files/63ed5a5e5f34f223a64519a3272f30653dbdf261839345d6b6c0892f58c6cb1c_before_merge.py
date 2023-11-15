    def history(self):
        """Returns computed metrics during training."""
        if self.is_trained_ is False:
            return {}
        return self.trainer.history