    def connect(self, **kwargs):
        """Connect to the device.

        Enables the device to send data to the host."""
        super().connect(**kwargs)
        self._configure_flow_control(clear_to_send=True)