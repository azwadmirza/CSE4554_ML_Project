    def stop(self):
        self.observer.stop()
        self.observer.join()
        del self.observer