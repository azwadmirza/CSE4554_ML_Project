    async def get_services(self) -> BleakGATTServiceCollection:
        """Get all services registered for this GATT server.

        Returns:
           A :py:class:`bleak.backends.service.BleakGATTServiceCollection` with this device's services tree.

        """
        if self._services != None:
            return self._services

        logger.debug("Retrieving services...")
        services = (
            await cbapp.central_manager_delegate.connected_peripheral_delegate.discoverServices()
        )

        for service in services:
            serviceUUID = service.UUID().UUIDString()
            logger.debug(
                "Retrieving characteristics for service {}".format(serviceUUID)
            )
            characteristics = await cbapp.central_manager_delegate.connected_peripheral_delegate.discoverCharacteristics_(
                service
            )

            self.services.add_service(BleakGATTServiceCoreBluetooth(service))

            for characteristic in characteristics:
                cUUID = characteristic.UUID().UUIDString()
                logger.debug(
                    "Retrieving descriptors for characteristic {}".format(cUUID)
                )
                descriptors = await cbapp.central_manager_delegate.connected_peripheral_delegate.discoverDescriptors_(
                    characteristic
                )

                self.services.add_characteristic(
                    BleakGATTCharacteristicCoreBluetooth(characteristic)
                )
                for descriptor in descriptors:
                    self.services.add_descriptor(
                        BleakGATTDescriptorCoreBluetooth(
                            descriptor, characteristic.UUID().UUIDString()
                        )
                    )
        self._services_resolved = True
        return self.services