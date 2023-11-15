    def __init__(self, *args, keep_local=False, stay_on_remote=False, is_default=False, **kwargs):
        super(RemoteProvider, self).__init__(
            *args, keep_local=keep_local, stay_on_remote=stay_on_remote, is_default=is_default, **kwargs
        )

        self._as = AzureStorageHelper(*args, **kwargs)