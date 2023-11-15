    async def disconnect(self) -> bool:
        logger.debug("Disconnecting from BLE device...")
        # Remove notifications
        # TODO: Make sure all notifications are removed prior to Dispose.
        # Dispose all components that we have requested and created.
        for service in self.services:
            # for characteristic in service.characteristics:
            #     for descriptor in characteristic.descriptors:
            #         descriptor.obj.Dispose()
            #     characteristic.obj.Dispose()
            service.obj.Dispose()
        self.services = BleakGATTServiceCollection()
        self._requester.Dispose()
        self._requester = None

        return not await self.is_connected()