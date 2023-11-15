    def __init__(self, namespace, session=None, **kwargs):
        self.conf = {'namespace': namespace}
        self.conf.update(kwargs)
        self._volume = None
        self._event = None
        self._cluster = None
        self._meta0 = None
        self.session = session