    def __init__(self, *args, **kwargs) -> None:
        kwargs['client_type'] = 's3'

        self.extra_args = {}
        if 'extra_args' in kwargs:
            self.extra_args = kwargs['extra_args']
            if not isinstance(self.extra_args, dict):
                raise ValueError(f"extra_args '{self.extra_args!r}' must be of type {dict}")
            del kwargs['extra_args']

        self.transfer_config = TransferConfig()
        if 'transfer_config_args' in kwargs:
            transport_config_args = kwargs['transfer_config_args']
            if not isinstance(transport_config_args, dict):
                raise ValueError(f"transfer_config_args '{transport_config_args!r} must be of type {dict}")
            self.transfer_config = TransferConfig(**transport_config_args)
            del kwargs['transfer_config_args']

        super().__init__(*args, **kwargs)