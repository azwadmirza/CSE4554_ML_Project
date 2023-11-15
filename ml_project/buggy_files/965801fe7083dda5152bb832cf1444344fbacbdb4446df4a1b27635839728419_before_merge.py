    def compare(self, action: int, checksum: bytes) -> bool:
        if self.action != action or self.checksum != checksum:
            return False
        if utime.ticks_ms() >= self.deadline:
            if self.workflow is not None:
                loop.close(self.workflow)
            return False
        return True