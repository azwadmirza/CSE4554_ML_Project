    def __init__(self, cmd, payload, operation):
        self._cmd = cmd
        self._operation = operation
        self._resource_group = None
        self._resource_name = None
        self._model_name = None
        self._model_path = None
        self._payload = payload
        self.last_saved = None
        self._resolve_model()