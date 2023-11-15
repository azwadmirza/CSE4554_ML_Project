    def stop(self):
        """Stop the hotword engine.

        Clean up Porcupine library.
        """
        if self.porcupine is not None:
            self.porcupine.delete()