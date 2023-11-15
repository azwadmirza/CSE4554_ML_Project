    def is_connected(self) -> bool:
        return self.transport is not None and not self.transport.is_closing()