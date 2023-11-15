    def __init__(self, namespace, endpoint=None, session=None):
        self.conf = {'namespace': namespace}
        self._volume = None
        self._event = None
        self._cluster = None
        self._meta0 = None
        self.session = session