    def __init__(
        self, *args, stay_on_remote=False, **kwargs
    ):  # this method is evaluated when instantiating this class
        super(RemoteProvider, self).__init__(
            *args, stay_on_remote=stay_on_remote, **kwargs
        )  # in addition to methods provided by AbstractRemoteProvider, we add these in

        self._s3c = S3Helper(*args, **kwargs)  # _private variable by convention