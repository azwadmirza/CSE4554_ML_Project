    def stop(self):
        if self.porcupine is not None:
            self.porcupine.delete()