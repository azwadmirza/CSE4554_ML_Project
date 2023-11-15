    def connect(self, **kwargs):
        """Connect to the device."""
        super().connect(**kwargs)
        ids = f'vid{self.vendor_id:04x}_pid{self.product_id:04x}'
        # must use the HID path because there is no serial number; however,
        # these can be quite long on Windows and macOS, so only take the
        # numbers, since they are likely the only parts that vary between two
        # devices of the same model
        loc = 'loc' + '_'.join((num.decode() for num in re.findall(b'\\d+', self.address)))
        self._data = RuntimeStorage(key_prefixes=[ids, loc])
        self._sequence = _sequence(self._data)