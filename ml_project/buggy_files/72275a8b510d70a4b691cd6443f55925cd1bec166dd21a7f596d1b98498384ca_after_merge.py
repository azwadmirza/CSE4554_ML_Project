        def blocking_call():
            result = self._check_authentication()
            return method(*args, **kwargs) if result is None else result