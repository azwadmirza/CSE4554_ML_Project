        def wrapper(self, *args, **kwargs):
            if self.is_remote:
                if hasattr(self.remote_object, func.__name__):
                    return getattr(self.remote_object, func.__name__)(*args, **kwargs)
            return func(self, *args, **kwargs)