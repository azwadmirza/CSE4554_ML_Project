    async def _handle_event(self, event):
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

        async def _refresh_if_no_audiopush(already_refreshed=False):
            email = self._login.email
            seen_commands = (
                self.hass.data[DATA_ALEXAMEDIA]["accounts"][email][
                    "websocket_commands"
                ].keys()
                if "websocket_commands"
                in (self.hass.data[DATA_ALEXAMEDIA]["accounts"][email])
                else None
            )
            if (
                not already_refreshed
                and seen_commands
                and not (
                    "PUSH_AUDIO_PLAYER_STATE" in seen_commands
                    or "PUSH_MEDIA_CHANGE" in seen_commands
                    or "PUSH_MEDIA_PROGRESS_CHANGE" in seen_commands
                )
            ):
                # force refresh if player_state update not found, see #397
                _LOGGER.debug(
                    "%s: No PUSH_AUDIO_PLAYER_STATE/"
                    "PUSH_MEDIA_CHANGE/PUSH_MEDIA_PROGRESS_CHANGE in %s;"
                    "forcing refresh",
                    hide_email(email),
                    seen_commands,
                )
                await self.async_update()

        try:
            if not self.enabled:
                return
        except AttributeError:
            pass
        already_refreshed = False
        event_serial = None
        if "last_called_change" in event:
            event_serial = (
                event["last_called_change"]["serialNumber"]
                if event["last_called_change"]
                else None
            )
        elif "bluetooth_change" in event:
            event_serial = (
                event["bluetooth_change"]["deviceSerialNumber"]
                if event["bluetooth_change"]
                else None
            )
        elif "player_state" in event:
            event_serial = (
                event["player_state"]["dopplerId"]["deviceSerialNumber"]
                if event["player_state"]
                else None
            )
        elif "queue_state" in event:
            event_serial = (
                event["queue_state"]["dopplerId"]["deviceSerialNumber"]
                if event["queue_state"]
                else None
            )
        elif "push_activity" in event:
            event_serial = (
                event.get("push_activity", {}).get("key", {}).get("serialNumber")
            )
        if not event_serial:
            return
        self.available = True
        self.async_schedule_update_ha_state()
        if "last_called_change" in event:
            if event_serial == self.device_serial_number or any(
                item["serialNumber"] == event_serial for item in self._app_device_list
            ):
                _LOGGER.debug(
                    "%s is last_called: %s",
                    self.name,
                    hide_serial(self.device_serial_number),
                )
                self._last_called = True
                self._last_called_timestamp = event["last_called_change"]["timestamp"]
            else:
                self._last_called = False
            if self.hass and self.async_schedule_update_ha_state:
                email = self._login.email
                force_refresh = not (
                    self.hass.data[DATA_ALEXAMEDIA]["accounts"][email]["websocket"]
                )
                self.async_schedule_update_ha_state(force_refresh=force_refresh)
        elif "bluetooth_change" in event:
            if event_serial == self.device_serial_number:
                _LOGGER.debug(
                    "%s bluetooth_state update: %s",
                    self.name,
                    hide_serial(event["bluetooth_change"]),
                )
                self._bluetooth_state = event["bluetooth_change"]
                # the setting of bluetooth_state is not consistent as this
                # takes from the event instead of the hass storage. We're
                # setting the value twice. Architectually we should have a
                # single authorative source of truth.
                self._source = await self._get_source()
                self._source_list = await self._get_source_list()
                if self.hass and self.async_schedule_update_ha_state:
                    self.async_schedule_update_ha_state()
        elif "player_state" in event:
            player_state = event["player_state"]
            if event_serial == self.device_serial_number:
                if "audioPlayerState" in player_state:
                    _LOGGER.debug(
                        "%s state update: %s",
                        self.name,
                        player_state["audioPlayerState"],
                    )
                    # allow delay before trying to refresh to avoid http 400 errors
                    await asyncio.sleep(2)
                    await self.async_update()
                    already_refreshed = True
                elif "mediaReferenceId" in player_state:
                    _LOGGER.debug(
                        "%s media update: %s",
                        self.name,
                        player_state["mediaReferenceId"],
                    )
                    await self.async_update()
                    already_refreshed = True
                elif "volumeSetting" in player_state:
                    _LOGGER.debug(
                        "%s volume updated: %s",
                        self.name,
                        player_state["volumeSetting"],
                    )
                    self._media_vol_level = player_state["volumeSetting"] / 100
                    if self.hass and self.async_schedule_update_ha_state:
                        self.async_schedule_update_ha_state()
                elif "dopplerConnectionState" in player_state:
                    self.available = player_state["dopplerConnectionState"] == "ONLINE"
                    if self.hass and self.async_schedule_update_ha_state:
                        self.async_schedule_update_ha_state()
                await _refresh_if_no_audiopush(already_refreshed)
        elif "push_activity" in event:
            if self.state in {STATE_IDLE, STATE_PAUSED, STATE_PLAYING}:
                _LOGGER.debug(
                    "%s checking for potential state update due to push activity on %s",
                    self.name,
                    hide_serial(event_serial),
                )
                # allow delay before trying to refresh to avoid http 400 errors
                await asyncio.sleep(2)
                await self.async_update()
                already_refreshed = True
        if "queue_state" in event:
            queue_state = event["queue_state"]
            if event_serial == self.device_serial_number:
                if (
                    "trackOrderChanged" in queue_state
                    and not queue_state["trackOrderChanged"]
                    and "loopMode" in queue_state
                ):
                    self._repeat = queue_state["loopMode"] == "LOOP_QUEUE"
                    _LOGGER.debug(
                        "%s repeat updated to: %s %s",
                        self.name,
                        self._repeat,
                        queue_state["loopMode"],
                    )
                elif "playBackOrder" in queue_state:
                    self._shuffle = queue_state["playBackOrder"] == "SHUFFLE_ALL"
                    _LOGGER.debug(
                        "%s shuffle updated to: %s %s",
                        self.name,
                        self._shuffle,
                        queue_state["playBackOrder"],
                    )
                await _refresh_if_no_audiopush(already_refreshed)