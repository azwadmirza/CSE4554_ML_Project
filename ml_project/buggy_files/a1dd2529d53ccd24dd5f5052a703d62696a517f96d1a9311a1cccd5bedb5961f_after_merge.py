    def name(self) -> str:
        if self.offline_mode:
            return 'offline-name'
        else:
            return self.experiment.name