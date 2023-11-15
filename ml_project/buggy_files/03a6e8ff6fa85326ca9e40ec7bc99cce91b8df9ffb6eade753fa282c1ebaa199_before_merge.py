    def _handle_event(self, event):
        """Handle events.

        This will update PUSH_MEDIA_QUEUE_CHANGE events to see if the switch
        should be updated.
        """
        try:
            if not self.enabled:
                return
        except AttributeError:
            pass
        if "queue_state" in event.data:
            queue_state = event.data["queue_state"]
            if queue_state["dopplerId"]["deviceSerialNumber"] == self._client.unique_id:
                self._state = getattr(self._client, self._switch_property)
                self.async_schedule_update_ha_state()