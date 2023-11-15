    def flush(self, at_exit=False):
        """Flushes the current command buffer to disk.

        Parameters
        ----------
        at_exit : bool, optional
            Whether the JsonHistoryFlusher should act as a thread in the
            background, or execute immediately and block.

        Returns
        -------
        hf : JsonHistoryFlusher or None
            The thread that was spawned to flush history
        """
        if len(self.buffer) == 0:
            return

        def skip(num):
            self._skipped += num

        hf = JsonHistoryFlusher(
            self.filename,
            tuple(self.buffer),
            self._queue,
            self._cond,
            at_exit=at_exit,
            skip=skip,
        )
        self.buffer = []
        return hf