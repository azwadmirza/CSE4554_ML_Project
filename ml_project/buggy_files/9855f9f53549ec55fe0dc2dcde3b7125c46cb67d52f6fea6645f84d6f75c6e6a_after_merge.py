    def _handle_event(self, event):
        """Handle events.

        This will update last_called and player_state events.
        Each MediaClient reports if it's the last_called MediaClient and will
        listen for HA events to determine it is the last_called.
        When polling instead of websockets, all devices on same account will
        update to handle starting music with other devices. If websocket is on
        only the updated alexa will update.
        Last_called events are only sent if it's a new device or timestamp.
        Without polling, we must schedule the HA update manually.
        https://developers.home-assistant.io/docs/en/entity_index.html#subscribing-to-updates
        The difference between self.update and self.schedule_update_ha_state
        is self.update will pull data from Amazon, while schedule_update
        assumes the MediaClient state is already updated.
        """
        if 'last_called_change' in event.data:
            if (event.data['last_called_change']['serialNumber'] ==
                    self.device_serial_number):
                _LOGGER.debug("%s is last_called: %s", self.name,
                              hide_serial(self.device_serial_number))
                self._last_called = True
            else:
                self._last_called = False
            if (self.hass and self.schedule_update_ha_state):
                email = self._login.email
                force_refresh = not (self.hass.data[DATA_ALEXAMEDIA]
                                     ['accounts'][email]['websocket'])
                self.schedule_update_ha_state(force_refresh=force_refresh)
        elif 'player_state' in event.data:
            player_state = event.data['player_state']
            if (player_state['dopplerId']
                    ['deviceSerialNumber'] == self.device_serial_number):
                if 'audioPlayerState' in player_state:
                    _LOGGER.debug("%s state update: %s",
                                  self.name,
                                  player_state['audioPlayerState'])
                    self.update()  # refresh is necessary to pull all data
                elif 'volumeSetting' in player_state:
                    _LOGGER.debug("%s volume updated: %s",
                                  self.name,
                                  player_state['volumeSetting'])
                    self._media_vol_level = player_state['volumeSetting']/100
                    if (self.hass and self.schedule_update_ha_state):
                        self.schedule_update_ha_state()
                elif 'dopplerConnectionState' in player_state:
                    self._available = (player_state['dopplerConnectionState']
                                       == "ONLINE")
                    if (self.hass and self.schedule_update_ha_state):
                        self.schedule_update_ha_state()