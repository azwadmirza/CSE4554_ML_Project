    async def get_services(self) -> BleakGATTServiceCollection:
        """Get all services registered for this GATT server.

        Returns:
           A :py:class:`bleak.backends.service.BleakGATTServiceCollection` with this device's services tree.

        """
        if self._services_resolved:
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

        # There is no guarantee that services are listed before characteristics
        # Managed Objects dict.
        # Need multiple iterations to construct the Service Collection

        _chars, _descs = [], []

        for object_path, interfaces in objs.items():
            logger.debug(utils.format_GATT_object(object_path, interfaces))
            if defs.GATT_SERVICE_INTERFACE in interfaces:
                service = interfaces.get(defs.GATT_SERVICE_INTERFACE)
                self.services.add_service(
                    BleakGATTServiceBlueZDBus(service, object_path)
                )
            elif defs.GATT_CHARACTERISTIC_INTERFACE in interfaces:
                char = interfaces.get(defs.GATT_CHARACTERISTIC_INTERFACE)
                _chars.append([char, object_path])
            elif defs.GATT_DESCRIPTOR_INTERFACE in interfaces:
                desc = interfaces.get(defs.GATT_DESCRIPTOR_INTERFACE)
                _descs.append([desc, object_path])

        for char, object_path in _chars:
            _service = list(
                filter(lambda x: x.path == char["Service"], self.services)
            )
            self.services.add_characteristic(
                BleakGATTCharacteristicBlueZDBus(
                    char, object_path, _service[0].uuid
                )
            )
            self._char_path_to_uuid[object_path] = char.get("UUID")

        for desc, object_path in _descs:
            _characteristic = list(
                filter(
                    lambda x: x.path == desc["Characteristic"],
                    self.services.characteristics.values(),
                )
            )
            self.services.add_descriptor(
                BleakGATTDescriptorBlueZDBus(
                    desc, object_path, _characteristic[0].uuid
                )
            )

        self._services_resolved = True
        return self.services