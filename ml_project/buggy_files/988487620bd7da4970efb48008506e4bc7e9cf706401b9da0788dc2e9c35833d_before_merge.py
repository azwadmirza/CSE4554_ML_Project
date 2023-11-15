    async def async_update(self):
        """Get the latest details on a media player.

        Because media players spend the majority of time idle, an adaptive
        update should be used to avoid flooding Amazon focusing on known
        play states. An initial version included an update_devices call on
        every update. However, this quickly floods the network for every new
        device added. This should only call refresh() to call the AlexaAPI.
        """
        try:
            if not self.enabled:
                return
        except AttributeError:
            pass
        email = self._login.email
        if (
            self.entity_id is None  # Device has not initialized yet
            or email not in self.hass.data[DATA_ALEXAMEDIA]["accounts"]
            or self._login.session.closed
        ):
            return
        device = self.hass.data[DATA_ALEXAMEDIA]["accounts"][email]["devices"][
            "media_player"
        ][self.unique_id]
        seen_commands = (
            self.hass.data[DATA_ALEXAMEDIA]["accounts"][email][
                "websocket_commands"
            ].keys()
            if "websocket_commands"
            in (self.hass.data[DATA_ALEXAMEDIA]["accounts"][email])
            else None
        )
        await self.refresh(  # pylint: disable=unexpected-keyword-arg
            device, no_throttle=True
        )
        websocket_enabled = self.hass.data[DATA_ALEXAMEDIA]["accounts"][email].get(
            "websocket"
        )
        if (
            self.state in [STATE_PLAYING]
            and
            #  only enable polling if websocket not connected
            (
                not websocket_enabled
                or not seen_commands
                or not (
                    "PUSH_AUDIO_PLAYER_STATE" in seen_commands
                    or "PUSH_MEDIA_CHANGE" in seen_commands
                    or "PUSH_MEDIA_PROGRESS_CHANGE" in seen_commands
                )
            )
        ):
            self._should_poll = False  # disable polling since manual update
            if (
                self._last_update == 0
                or util.dt.as_timestamp(util.utcnow())
                - util.dt.as_timestamp(self._last_update)
                > PLAY_SCAN_INTERVAL
            ):
                _LOGGER.debug(
                    "%s playing; scheduling update in %s seconds",
                    self.name,
                    PLAY_SCAN_INTERVAL,
                )
                async_call_later(
                    self.hass,
                    PLAY_SCAN_INTERVAL,
                    lambda _: self.async_schedule_update_ha_state(force_refresh=True),
                )
        elif self._should_poll:  # Not playing, one last poll
            self._should_poll = False
            if not websocket_enabled:
                _LOGGER.debug(
                    "Disabling polling and scheduling last update in"
                    " 300 seconds for %s",
                    self.name,
                )
                async_call_later(
                    self.hass,
                    300,
                    lambda _: self.async_schedule_update_ha_state(force_refresh=True),
                )
            else:
                _LOGGER.debug("Disabling polling for %s", self.name)
        self._last_update = util.utcnow()
        self.async_schedule_update_ha_state()