    def version(self) -> str:
        if self.mode == 'offline':
            return 'offline-id-1234'
        else:
            return self.experiment.id