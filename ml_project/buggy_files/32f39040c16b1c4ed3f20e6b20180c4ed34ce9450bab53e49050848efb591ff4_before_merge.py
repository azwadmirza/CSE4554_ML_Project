    def __init__(self, address, loop=None, **kwargs):
        self.address = address
        self.loop = loop if loop else asyncio.get_event_loop()
        self.services = {}
        self.characteristics = {}

        self._services_resolved = False
        self._notification_callbacks = {}