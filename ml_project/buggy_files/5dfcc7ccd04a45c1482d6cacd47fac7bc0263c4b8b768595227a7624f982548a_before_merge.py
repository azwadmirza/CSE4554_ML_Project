    def __init__(
        self,
        *,
        bucket_name: str,
        prefix: str,
        aws_conn_id: str = 'aws_default',
        verify: Optional[Union[bool, str]] = None,
        inactivity_period: float = 60 * 60,
        min_objects: int = 1,
        previous_objects: Optional[Set[str]] = None,
        allow_delete: bool = True,
        **kwargs,
    ) -> None:

        super().__init__(**kwargs)

        self.bucket = bucket_name
        self.prefix = prefix
        if inactivity_period < 0:
            raise ValueError("inactivity_period must be non-negative")
        self.inactivity_period = inactivity_period
        self.min_objects = min_objects
        self.previous_objects = previous_objects or set()
        self.inactivity_seconds = 0
        self.allow_delete = allow_delete
        self.aws_conn_id = aws_conn_id
        self.verify = verify
        self.last_activity_time: Optional[datetime] = None