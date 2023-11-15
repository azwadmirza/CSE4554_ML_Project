    def close(self):
        # One second to send any queued messages
        self._context.destroy(1 * 1000)