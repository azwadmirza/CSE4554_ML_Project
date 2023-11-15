    def __init__(self, cmd, payload, operation):
        self._cmd = cmd
        self._operation = operation
        self._resource_group = None
        self._resource_name = None
        self._model_type = self._get_model_type()
        self._payload = payload
        self._last_touched = str(datetime.datetime.now())