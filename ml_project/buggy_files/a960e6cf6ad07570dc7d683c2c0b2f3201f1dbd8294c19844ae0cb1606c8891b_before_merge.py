    async def get_services(self) -> dict:
        # Return a list of all services for the device.
        if self.services:
            return self.services
        else:
            logger.debug("Get Services...")
            services = await wrap_Task(
                self._bridge.GetGattServicesAsync(self._requester), loop=self.loop
            )
            if services.Status == GattCommunicationStatus.Success:
                self.services = {s.Uuid.ToString(): s for s in services.Services}
            else:
                raise BleakDotNetTaskError("Could not get GATT services.")

            # TODO: Could this be sped up?
            await asyncio.gather(
                *[
                    asyncio.ensure_future(self._get_chars(service), loop=self.loop)
                    for service_uuid, service in self.services.items()
                ]
            )
            self._services_resolved = True
            return self.services