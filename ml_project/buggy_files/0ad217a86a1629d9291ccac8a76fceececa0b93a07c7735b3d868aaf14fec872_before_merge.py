    def _handle_event(self, event):
        """Handle events.

        This will update PUSH_NOTIFICATION_CHANGE events to see if the sensor
        should be updated.
        """
        try:
            if not self.enabled:
                return
        except AttributeError:
            pass
        if "notification_update" in event.data:
            if (
                event.data["notification_update"]["dopplerId"]["deviceSerialNumber"]
                == self._client.unique_id
            ):
                _LOGGER.debug("Updating sensor %s", self.name)
                self.async_schedule_update_ha_state(True)