    def __init__(self, device, device_type, xiaomi_hub):
        """Initialize the Xiaomi device."""
        self._state = None
        self._is_available = True
        self._sid = device['sid']
        self._name = '{}_{}'.format(device_type, self._sid)
        self._type = device_type
        self._write_to_hub = xiaomi_hub.write_to_hub
        self._get_from_hub = xiaomi_hub.get_from_hub
        self._device_state_attributes = {}
        self._remove_unavailability_tracker = None
        self._xiaomi_hub = xiaomi_hub
        self.parse_data(device['data'], device['raw_data'])
        self.parse_voltage(device['data'])

        if hasattr(self, '_data_key') \
                and self._data_key:  # pylint: disable=no-member
            self._unique_id = "{}{}".format(
                self._data_key,  # pylint: disable=no-member
                self._sid)
        else:
            self._unique_id = "{}{}".format(self._type, self._sid)