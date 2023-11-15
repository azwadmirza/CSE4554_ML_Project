    def stop(self):
        if self.observer is not None:
            # This is required to avoid showing an error when closing
            # projects.
            # Fixes spyder-ide/spyder#14107
            try:
                self.observer.stop()
                self.observer.join()
                del self.observer
            except RuntimeError:
                pass