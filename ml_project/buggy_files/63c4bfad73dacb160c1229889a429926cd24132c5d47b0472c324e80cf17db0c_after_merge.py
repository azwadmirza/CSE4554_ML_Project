    def _handle_event(self, event):
        """Handle events.

        This will update PUSH_EQUALIZER_STATE_CHANGE events to see if the DND switch
        should be updated.
        """
        try:
            if not self.enabled:
                return
        except AttributeError:
            pass
        if "player_state" in event:
            queue_state = event["player_state"]
            if queue_state["dopplerId"]["deviceSerialNumber"] == self._client.unique_id:
                self._state = getattr(self._client, self._switch_property)
                self.async_schedule_update_ha_state()