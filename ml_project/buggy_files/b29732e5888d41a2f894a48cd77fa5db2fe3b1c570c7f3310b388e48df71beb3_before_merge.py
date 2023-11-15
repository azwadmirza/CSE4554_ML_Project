    def _properties_changed_callback(self, message):
        """Notification handler.

        In the BlueZ DBus API, notifications come as
        PropertiesChanged callbacks on the GATT Characteristic interface
        that StartNotify has been called on.

        Args:
            message (): The PropertiesChanged DBus signal message relaying
                the new data on the GATT Characteristic.

        """
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