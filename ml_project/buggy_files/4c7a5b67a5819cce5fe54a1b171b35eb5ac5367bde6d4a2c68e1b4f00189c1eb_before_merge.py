    def async_call(self, name, *args, **kwargs):
        """Call the actual HTTP method, if available."""
        try:
            method = getattr(self, 'http_' + name)
        except AttributeError:
            raise HTTPError(405, '{name} method is not allowed'.format(name=name.upper()))

        def blocking_call():
            try:
                return method(*args, **kwargs)
            except Exception as error:
                self._handle_request_exception(error)

        return IOLoop.current().run_in_executor(executor, blocking_call)