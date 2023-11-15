    def __call__(self, progress):
        assert progress >= 0.0
#         assert progress <= 1.0 # TODO restore this assert when the progress > 1 bug is fixed
#         assert (progress == 0 and self.prev_progress == 1.0) or (progress >= self.prev_progress)
        
        if progress > 1.0:
            log.debug("progress out of bounds: %.3f", progress)

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
                self._finish()
                if self.backwards_progress:
                    log.warning("Progress went backwards!")