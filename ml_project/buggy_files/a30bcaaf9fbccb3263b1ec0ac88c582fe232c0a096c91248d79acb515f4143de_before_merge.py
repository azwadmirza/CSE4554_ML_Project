    async def get_services(self) -> dict:
        """Get all services registered for this GATT server.

        Returns:
            Dictionary of all service UUIDs as keys and
            service object's properties as values.

        """
        if self.services:
            return self.services

        while True:
            properties = await self._get_device_properties()
            services_resolved = properties.get("ServicesResolved", False)
            if services_resolved:
                break
            await asyncio.sleep(0.02, loop=self.loop)

        logger.debug("Get Services...")
        objs = await get_managed_objects(
            self._bus, self.loop, self._device_path + "/service"
        )
        self.services = {}
        self.characteristics = {}
        self._descriptors = {}
        for object_path, interfaces in objs.items():
            logger.debug(utils.format_GATT_object(object_path, interfaces))
            if defs.GATT_SERVICE_INTERFACE in interfaces:
                service = interfaces.get(defs.GATT_SERVICE_INTERFACE)
                self.services[service.get("UUID")] = service
                self.services[service.get("UUID")]["Path"] = object_path
            elif defs.GATT_CHARACTERISTIC_INTERFACE in interfaces:
                char = interfaces.get(defs.GATT_CHARACTERISTIC_INTERFACE)
                self.characteristics[char.get("UUID")] = char
                self.characteristics[char.get("UUID")]["Path"] = object_path
                self._char_path_to_uuid[object_path] = char.get("UUID")
            elif defs.GATT_DESCRIPTOR_INTERFACE in interfaces:
                desc = interfaces.get(defs.GATT_DESCRIPTOR_INTERFACE)
                self._descriptors[desc.get("UUID")] = desc
                self._descriptors[desc.get("UUID")]["Path"] = object_path

        self._services_resolved = True
        return self.services