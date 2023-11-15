    def __call__(self, progress):
        assert progress >= 0.0

        # Cap progress at 1.0.        
        if progress > 1.0:
            progress = 1.0
            LOG.debug("progress out of bounds: %.3f", progress)

        # Reset state on 0.0
        if progress == 0.0:
            self._start()

        # Check for backwards progress
        if progress < self.prev_progress:
            self.backwards_progress = True
        self.prev_progress = progress

        # print progress bar
        if not self.done:
            self._update(progress)

            # Finish on 1.0
            if progress >= 1.0:
                self.done = True
                self._finish()
                if self.backwards_progress:
                    LOG.debug("Progress went backwards!")