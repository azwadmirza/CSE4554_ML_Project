    def driver_removed_handler(self, unused_channel, data):
        """Handle a notification that a driver has been removed.

        This releases any GPU resources that were reserved for that driver in
        Redis.
        """
        message = DriverTableMessage.GetRootAsDriverTableMessage(data, 0)
        driver_id = message.DriverId()
        log.info(
            "Driver {} has been removed.".format(binary_to_hex(driver_id)))

        self._clean_up_entries_for_driver(driver_id)