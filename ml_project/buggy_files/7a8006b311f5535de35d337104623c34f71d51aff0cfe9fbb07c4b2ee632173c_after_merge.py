    def stop(self):
        if self.observer is not None:
            self.observer.stop()
            self.observer.join()
            del self.observer