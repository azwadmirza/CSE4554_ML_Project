    def version(self) -> str:
        if self.offline_mode:
            return 'offline-id-1234'
        else:
            return self.experiment.id