    def __init__(self, *args, **kwargs) -> None:
        kwargs['client_type'] = 's3'

        self.extra_args = {}
        if 'extra_args' in kwargs:
            self.extra_args = kwargs['extra_args']
            if not isinstance(self.extra_args, dict):
                raise ValueError(f"extra_args '{self.extra_args!r}' must be of type {dict}")
            del kwargs['extra_args']

        super().__init__(*args, **kwargs)