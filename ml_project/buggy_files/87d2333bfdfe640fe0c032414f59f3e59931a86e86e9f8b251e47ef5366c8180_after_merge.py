    async def async_alarm_disarm(self, code=None) -> None:
        # pylint: disable=unexpected-keyword-arg
        """Send disarm command."""
        await self._async_alarm_set(STATE_ALARM_DISARMED)