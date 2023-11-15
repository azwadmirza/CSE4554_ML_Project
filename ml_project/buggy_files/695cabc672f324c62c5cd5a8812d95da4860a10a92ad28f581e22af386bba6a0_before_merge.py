    def __init__(self, address, loop=None, **kwargs):
        super(BleakClientBlueZDBus, self).__init__(address, loop, **kwargs)
        self.device = kwargs.get("device") if kwargs.get("device") else "hci0"
        self.address = address

        # Backend specific, TXDBus objects and data
        self._device_path = None
        self._bus = None
        self._descriptors = {}
        self._rules = {}

        self._char_path_to_uuid = {}