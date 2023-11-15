    def stop(self):
        """Stop notifying Listeners when new :class:`~can.Message` objects arrive
         and call :meth:`~can.Listener.stop` on each Listener."""
        self.running.clear()
        if self.timeout is not None:
            self._reader.join(self.timeout + 0.1)