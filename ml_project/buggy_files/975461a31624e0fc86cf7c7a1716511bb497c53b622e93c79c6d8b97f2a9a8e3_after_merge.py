    def __init__(self, **kwargs):
        engine = kwargs.pop('engine', None)
        self._endpoint = None
        self._session_id = uuid.uuid4()
        self._context = LocalContext(self)
        self._executor = Executor(engine=engine, storage=self._context)

        self._mut_tensor = dict()
        self._mut_tensor_data = dict()

        if kwargs:
            unexpected_keys = ', '.join(list(kwargs.keys()))
            raise TypeError(f'Local session got unexpected arguments: {unexpected_keys}')