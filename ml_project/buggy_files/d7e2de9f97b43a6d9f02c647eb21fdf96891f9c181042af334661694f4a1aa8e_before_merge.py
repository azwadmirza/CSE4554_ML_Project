    def __init__(self, address_or_ble_device: Union[BLEDevice, str], **kwargs):
        super(BleakClientDotNet, self).__init__(address_or_ble_device, **kwargs)

        # Backend specific. Python.NET objects.
        if isinstance(address_or_ble_device, BLEDevice):
            self._device_info = address_or_ble_device.details.BluetoothAddress
        else:
            self._device_info = None
        self._requester = None
        self._bridge = None

        self._address_type = (
            kwargs["address_type"]
            if "address_type" in kwargs
            and kwargs["address_type"] in ("public", "random")
            else None
        )