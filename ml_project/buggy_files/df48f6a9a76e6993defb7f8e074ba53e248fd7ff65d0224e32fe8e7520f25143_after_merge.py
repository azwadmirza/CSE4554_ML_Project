    def close(self):
        if self._context is not None:
            # One second to send any queued messages
            self._context.destroy(1 * 1000)