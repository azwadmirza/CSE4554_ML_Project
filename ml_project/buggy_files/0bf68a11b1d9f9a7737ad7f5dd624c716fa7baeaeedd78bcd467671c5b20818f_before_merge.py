    def _wrapped(*args, **kwargs):
        _kernel_mode.eager = False
        return_value = func(*args, **kwargs)
        _kernel_mode.eager = None
        return return_value