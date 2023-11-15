    def async_call(self, name, *args, **kwargs):
        """Call the actual HTTP method, if available."""
        try:
            method = getattr(self, 'http_' + name)
        except AttributeError:
            raise HTTPError(405)

        def blocking_call():
            result = self._check_authentication()
            return method(*args, **kwargs) if result is None else result

        return IOLoop.current().run_in_executor(executor, blocking_call)