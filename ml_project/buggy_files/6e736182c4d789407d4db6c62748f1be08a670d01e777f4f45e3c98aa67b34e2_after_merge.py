    def get(self, timeout=None, propagate=True, interval=0.5,
            callback=None, no_ack=True, on_message=None,
            disable_sync_subtasks=True, on_interval=None):
        """See :meth:`join`.

        This is here for API compatibility with :class:`AsyncResult`,
        in addition it uses :meth:`join_native` if available for the
        current result backend.
        """
        if self._cache is not None:
            return self._cache
        return (self.join_native if self.supports_native_join else self.join)(
            timeout=timeout, propagate=propagate,
            interval=interval, callback=callback, no_ack=no_ack,
            on_message=on_message, disable_sync_subtasks=disable_sync_subtasks,
            on_interval=on_interval,
        )