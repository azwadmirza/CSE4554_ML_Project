    def __init__(self, **kwargs):
        if not ray.is_initialized():
            ray.init(**kwargs)
        self._session_id = uuid.uuid4()
        self._executor = RayExecutor(storage=RayStorage())