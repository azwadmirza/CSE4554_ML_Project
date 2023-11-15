    def __init__(self, *args, stay_on_remote=False, **kwargs):
        super(RemoteProvider, self).__init__(
            *args, stay_on_remote=stay_on_remote, **kwargs
        )

        self._as = AzureStorageHelper(*args, **kwargs)