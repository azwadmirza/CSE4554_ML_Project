    async def disconnect(self) -> bool:
        logger.debug("Disconnecting from BLE device...")
        # Remove notifications
        # TODO: Make sure all notifications are removed prior to Dispose.
        # Dispose all components that we have requested and created.
        for service_uuid, service in self.services.items():
            service.Dispose()
        self.services = None
        self._requester.Dispose()
        self._requester = None

        return not await self.is_connected()