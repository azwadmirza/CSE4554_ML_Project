    def run(self):
        """Calls the :attr:`pooled_function` callable."""

        try:
            self._result = self.pooled_function(*self.args, **self.kwargs)

        except Exception as exc:
            self._exception = exc

        finally:
            self.done.set()