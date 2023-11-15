    def __init__(self, plugin, handler, dev_path, *, is_simulator=False):
        HardwareClientBase.__init__(self, plugin=plugin)
        self.device = plugin.device
        self.handler = handler

        # if we know what the (xfp, xpub) "should be" then track it here
        self._expected_device = None

        if is_simulator:
            self.dev = ElectrumColdcardDevice(dev_path, encrypt=True)
        else:
            # open the real HID device
            with self.device_manager().hid_lock:
                hd = hid.device(path=dev_path)
                hd.open_path(dev_path)

            self.dev = ElectrumColdcardDevice(dev=hd, encrypt=True)