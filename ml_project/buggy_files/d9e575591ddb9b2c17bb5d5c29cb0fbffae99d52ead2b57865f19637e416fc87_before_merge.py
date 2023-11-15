    async def connect(self, **kwargs) -> bool:
        """Connect to a specified Peripheral

        Keyword Args:
            timeout (float): Timeout for required ``discover`` call. Defaults to 2.0.

        Returns:
            Boolean representing connection status.
        """

        devices = await discover(timeout=kwargs.get("timeout", 5.0), loop=self.loop)
        sought_device = list(
            filter(lambda x: x.address.upper() == self.address.upper(), devices)
        )

        if len(sought_device):
            self._device_info = sought_device[0].details
        else:
            raise BleakError(
                "Device with address {} was not found".format(self.address)
            )

        logger.debug("Connecting to BLE device @ {}".format(self.address))

        await cbapp.central_manager_delegate.connect_(sought_device[0].details)

        # Now get services
        await self.get_services()

        return True