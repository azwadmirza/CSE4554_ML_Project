    def status(self):
        """The process current status as a STATUS_* constant."""
        try:
            return self._proc.status()
        except ZombieProcess:
            return STATUS_ZOMBIE