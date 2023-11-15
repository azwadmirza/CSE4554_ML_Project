    async def async_alarm_disarm(self, code=None) -> None:
        # pylint: disable=unexpected-keyword-arg
        """Send disarm command."""
        try:
            if not self.enabled:
                return
        except AttributeError:
            pass
        await self.alexa_api.set_guard_state(
            self._login, self._guard_entity_id, "ARMED_STAY"
        )
        await self.async_update(no_throttle=True)
        self.async_schedule_update_ha_state()