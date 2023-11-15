    def reps(self, repetitions: int) -> None:
        """Set the repetitions.

        Args:
            repetitions: The new repetitions.
        """
        if repetitions != self._reps:
            self._invalidate()
            self._reps = repetitions