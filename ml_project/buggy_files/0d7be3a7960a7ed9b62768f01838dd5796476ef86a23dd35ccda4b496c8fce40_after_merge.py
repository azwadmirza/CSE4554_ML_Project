    def __init__(self, applet):
        self._applet = applet
        self._config = Config("org.blueman.transfer")

        self._agent_path = '/org/blueman/obex_agent'

        self._agent = obex.Agent(self._agent_path)
        self._agent.connect('release', self._on_release)
        self._agent.connect('authorize', self._on_authorize)
        self._agent.connect('cancel', self._on_cancel)

        self._allowed_devices = []
        self._notification = None
        self._pending_transfer = None
        self.transfers = {}