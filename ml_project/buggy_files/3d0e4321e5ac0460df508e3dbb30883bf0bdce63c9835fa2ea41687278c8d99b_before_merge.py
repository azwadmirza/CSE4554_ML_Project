    async def async_alarm_arm_away(self, code=None) -> None:
        """Send arm away command."""
        # pylint: disable=unexpected-keyword-arg
        try:
            if not self.enabled:
                return
        except AttributeError:
            pass
        await self.alexa_api.set_guard_state(
            self._login, self._guard_entity_id, "ARMED_AWAY"
        )
        await self.async_update(no_throttle=True)
        self.async_schedule_update_ha_state()