    def name(self) -> str:
        if self.mode == 'offline':
            return 'offline-name'
        else:
            return self.experiment.name