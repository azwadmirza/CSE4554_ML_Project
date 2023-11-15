    def async_func(*args, **kwargs):
        warnings.warn('The @run_async decorator is deprecated. Use the `run_async` parameter of'
                      '`Dispatcher.add_handler` or `Dispatcher.run_async` instead.',
                      TelegramDeprecationWarning,
                      stacklevel=2)
        return Dispatcher.get_instance()._run_async(func, *args, update=None, error_handling=False,
                                                    **kwargs)