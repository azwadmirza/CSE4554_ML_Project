    def update_serial(self, new_serial):
        """Updates the serial number of a device.

        The "serial number" used with adb's `-s` arg is not necessarily the
        actual serial number. For remote devices, it could be a combination of
        host names and port numbers.

        This is used for when such identifier of remote devices changes during
        a test. For example, when a remote device reboots, it may come back
        with a different serial number.

        This is NOT meant for switching the object to represent another device.

        We intentionally did not make it a regular setter of the serial
        property so people don't accidentally call this without understanding
        the consequences.

        Args:
            new_serial: string, the new serial number for the same device.

        Raises:
            DeviceError: tries to update serial when any service is running.
        """
        new_serial = str(new_serial)
        if self.has_active_service:
            raise DeviceError(
                self,
                'Cannot change device serial number when there is service running.'
            )
        if self._debug_tag == self.serial:
            self._debug_tag = new_serial
        self._serial = new_serial
        self.adb.serial = new_serial
        self.fastboot.serial = new_serial