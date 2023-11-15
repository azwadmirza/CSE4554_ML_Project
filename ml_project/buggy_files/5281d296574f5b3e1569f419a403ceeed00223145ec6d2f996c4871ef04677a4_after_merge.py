    def _close(self, engine):
        if self.pbar:
            self.pbar.close()
        self.pbar = None