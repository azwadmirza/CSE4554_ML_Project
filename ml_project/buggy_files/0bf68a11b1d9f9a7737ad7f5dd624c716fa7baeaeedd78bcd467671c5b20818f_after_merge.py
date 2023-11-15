    def _wrapped(*args, **kwargs):
        try:
            _kernel_mode.eager = False
            return func(*args, **kwargs)
        finally:
            _kernel_mode.eager = None