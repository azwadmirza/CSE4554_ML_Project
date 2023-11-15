    def __init__(self, resource: str, event: str, **kwargs) -> None:

        if not resource:
            raise ValueError('Missing mandatory value for "resource"')
        if not event:
            raise ValueError('Missing mandatory value for "event"')
        if any(['.' in key for key in kwargs.get('attributes', dict()).keys()]) \
                or any(['$' in key for key in kwargs.get('attributes', dict()).keys()]):
            raise ValueError('Attribute keys must not contain "." or "$"')
        if isinstance(kwargs.get('value', None), int):
            kwargs['value'] = str(kwargs['value'])
        for attr in ['create_time', 'receive_time', 'last_receive_time']:
            if not isinstance(kwargs.get(attr), (datetime, NoneType)):  # type: ignore
                raise ValueError("Attribute '{}' must be datetime type".format(attr))

        timeout = kwargs.get('timeout') if kwargs.get('timeout') is not None else current_app.config['ALERT_TIMEOUT']
        try:
            timeout = int(timeout)  # type: ignore
        except ValueError:
            raise ValueError("Could not convert 'timeout' value of '{}' to an integer".format(timeout))
        if timeout < 0:
            raise ValueError("Invalid negative 'timeout' value ({})".format(timeout))

        self.id = kwargs.get('id', None) or str(uuid4())
        self.resource = resource
        self.event = event
        self.environment = kwargs.get('environment', None) or ''
        self.severity = kwargs.get('severity', None) or alarm_model.DEFAULT_NORMAL_SEVERITY
        self.correlate = kwargs.get('correlate', None) or list()
        if self.correlate and event not in self.correlate:
            self.correlate.append(event)
        self.status = kwargs.get('status', None) or alarm_model.DEFAULT_STATUS
        self.service = kwargs.get('service', None) or list()
        self.group = kwargs.get('group', None) or 'Misc'
        self.value = kwargs.get('value', None)
        self.text = kwargs.get('text', None) or ''
        self.tags = kwargs.get('tags', None) or list()
        self.attributes = kwargs.get('attributes', None) or dict()
        self.origin = kwargs.get('origin', None) or '{}/{}'.format(os.path.basename(sys.argv[0]), platform.uname()[1])
        self.event_type = kwargs.get('event_type', kwargs.get('type', None)) or 'exceptionAlert'
        self.create_time = kwargs.get('create_time', None) or datetime.utcnow()
        self.timeout = timeout
        self.raw_data = kwargs.get('raw_data', None)
        self.customer = kwargs.get('customer', None)

        self.duplicate_count = kwargs.get('duplicate_count', None)
        self.repeat = kwargs.get('repeat', None)
        self.previous_severity = kwargs.get('previous_severity', None)
        self.trend_indication = kwargs.get('trend_indication', None)
        self.receive_time = kwargs.get('receive_time', None) or datetime.utcnow()
        self.last_receive_id = kwargs.get('last_receive_id', None)
        self.last_receive_time = kwargs.get('last_receive_time', None)
        self.update_time = kwargs.get('update_time', None)
        self.history = kwargs.get('history', None) or list()