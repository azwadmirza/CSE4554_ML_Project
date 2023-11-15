    async def async_alarm_arm_away(self, code=None) -> None:
        """Send arm away command."""
        # pylint: disable=unexpected-keyword-arg
        await self._async_alarm_set(STATE_ALARM_ARMED_AWAY)