    def __init__(self, address, loop=None, **kwargs):
        super(BleakClientBlueZDBus, self).__init__(address, loop, **kwargs)
        self.device = kwargs.get("device") if kwargs.get("device") else "hci0"
        self.address = address

        # Backend specific, TXDBus objects and data
        self._device_path = None
        self._bus = None
        self._rules = {}
        self._subscriptions = list()

        self._disconnected_callback = None

        self._char_path_to_uuid = {}

        # We need to know BlueZ version since battery level characteristic
        # are stored in a separate DBus interface in the BlueZ >= 5.48.
        p = subprocess.Popen(["bluetoothctl", "--version"], stdout=subprocess.PIPE)
        out, _ = p.communicate()
        s = re.search(b"(\\d+).(\\d+)", out.strip(b"'"))
        self._bluez_version = tuple(map(int, s.groups()))