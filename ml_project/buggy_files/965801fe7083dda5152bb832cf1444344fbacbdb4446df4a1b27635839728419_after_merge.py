    def compare(self, action: int, checksum: bytes) -> bool:
        if self.action != action or self.checksum != checksum:
            return False
        if utime.ticks_ms() >= self.deadline:
            if self.workflow is not None:
                # We crossed the deadline, kill the running confirmation
                # workflow. `self.workflow` is reset in the finally
                # handler in `confirm_workflow`.
                loop.close(self.workflow)
            return False
        return True