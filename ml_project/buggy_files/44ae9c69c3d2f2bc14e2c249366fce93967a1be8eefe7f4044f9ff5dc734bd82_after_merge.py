    def _cancel_current_command(self, waiter):
        self._cancellations.add(self._loop.create_task(self._cancel(waiter)))