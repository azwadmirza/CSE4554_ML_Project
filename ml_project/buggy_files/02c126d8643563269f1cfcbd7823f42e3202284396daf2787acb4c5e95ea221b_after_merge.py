    def __init__(self, **kwargs):
        # as we cannot serialize fuse chunk for now,
        # we just disable numexpr for ray executor
        engine = kwargs.pop('engine', ['numpy', 'dataframe'])
        if not ray.is_initialized():
            ray.init(**kwargs)
        self._session_id = uuid.uuid4()
        self._executor = RayExecutor(engine=engine,
                                     storage=RayStorage())