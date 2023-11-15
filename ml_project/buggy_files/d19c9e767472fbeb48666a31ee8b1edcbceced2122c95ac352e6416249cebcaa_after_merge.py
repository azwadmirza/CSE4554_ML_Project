    def reps(self, repetitions: int) -> None:
        """Set the repetitions.

        Args:
            repetitions: The new repetitions.

        Raises:
            ValueError: If reps setter has parameter repetitions <= 0.
        """
        if repetitions <= 0:
            raise ValueError('The repetitions should be larger than or equal to 1')
        if repetitions != self._reps:
            self._invalidate()
            self._reps = repetitions