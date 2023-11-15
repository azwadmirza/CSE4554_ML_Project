    def _properties_changed_callback(self, message):
        """Notification handler.

        In the BlueZ DBus API, notifications come as
        PropertiesChanged callbacks on the GATT Characteristic interface
        that StartNotify has been called on.

        Args:
            message (): The PropertiesChanged DBus signal message relaying
                the new data on the GATT Characteristic.

        """

        logger.debug(
            "DBUS: path: {}, domain: {}, body: {}".format(
                message.path, message.body[0], message.body[1]
            )
        )

        if message.body[0] == defs.GATT_CHARACTERISTIC_INTERFACE:
            if message.path in self._notification_callbacks:
                logger.info(
                    "GATT Char Properties Changed: {0} | {1}".format(
                        message.path, message.body[1:]
                    )
                )
                self._notification_callbacks[message.path](
                    message.path, message.body[1]
                )
        elif message.body[0] == defs.DEVICE_INTERFACE:
            device_path = "/org/bluez/%s/dev_%s" % (
                self.device,
                self.address.replace(":", "_"),
            )
            if message.path.lower() == device_path.lower():
                message_body_map = message.body[1]
                if (
                    "Connected" in message_body_map
                    and not message_body_map["Connected"]
                ):
                    logger.debug("Device {} disconnected.".format(self.address))

                    self.loop.create_task(self._cleanup())

                    if self._disconnected_callback is not None:
                        self._disconnected_callback(self)