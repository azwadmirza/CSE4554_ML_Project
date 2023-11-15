    async def _async_alarm_set(self, command: Text = "", code=None) -> None:
        # pylint: disable=unexpected-keyword-arg
        """Send command."""
        self.check_login_changes()
        try:
            if not self.enabled:
                return
        except AttributeError:
            pass
        if command not in (STATE_ALARM_ARMED_AWAY, STATE_ALARM_DISARMED):
            _LOGGER.error("Invalid command: %s", command)
            return
        command_map = {STATE_ALARM_ARMED_AWAY: "AWAY", STATE_ALARM_DISARMED: "HOME"}
        available_media_players = list(
            filter(lambda x: x.state != STATE_UNAVAILABLE, self._media_players.values())
        )
        if available_media_players:
            _LOGGER.debug("Sending guard command to: %s", available_media_players[0])
            await available_media_players[0].alexa_api.set_guard_state(
                self._appliance_id.split("_")[2],
                command_map[command],
                queue_delay=self.hass.data[DATA_ALEXAMEDIA]["accounts"][self.email][
                    "options"
                ].get(CONF_QUEUE_DELAY, DEFAULT_QUEUE_DELAY),
            )
            await sleep(2)  # delay
        else:
            _LOGGER.debug("Performing static guard command")
            await self.alexa_api.static_set_guard_state(
                self._login, self._guard_entity_id, command
            )
        await self.async_update(no_throttle=True)
        self.async_schedule_update_ha_state()