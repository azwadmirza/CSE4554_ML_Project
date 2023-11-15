        def blocking_call():
            try:
                return method(*args, **kwargs)
            except Exception as error:
                self._handle_request_exception(error)