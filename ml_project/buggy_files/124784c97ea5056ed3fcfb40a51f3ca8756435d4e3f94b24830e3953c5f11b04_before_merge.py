    def release(self) -> None:
        self.semaphore.release()