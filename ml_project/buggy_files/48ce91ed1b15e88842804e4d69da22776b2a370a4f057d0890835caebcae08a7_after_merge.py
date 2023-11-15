    def __init__(self, origin: str=None, tags: List[str]=None, create_time: datetime=None, timeout: int=None, customer: str=None, **kwargs) -> None:

        timeout = timeout if timeout is not None else current_app.config['HEARTBEAT_TIMEOUT']
        try:
            timeout = int(timeout)
        except ValueError:
            raise ValueError("Could not convert 'timeout' value of '{}' to an integer".format(timeout))
        if timeout < 0:
            raise ValueError("Invalid negative 'timeout' value ({})".format(timeout))

        self.id = kwargs.get('id', str(uuid4()))
        self.origin = origin or '{}/{}'.format(os.path.basename(sys.argv[0]), platform.uname()[1])
        self.tags = tags or list()
        self.event_type = kwargs.get('event_type', kwargs.get('type', None)) or 'Heartbeat'
        self.create_time = create_time or datetime.utcnow()
        self.timeout = timeout
        self.receive_time = kwargs.get('receive_time', None) or datetime.utcnow()
        self.customer = customer