    def _update_recurring_alarm(self, value):
        _LOGGER.debug("value %s", value)
        alarm = value[1][self._sensor_property]
        alarm_on = value[1]["status"] == "ON"
        recurring_pattern = value[1]["recurringPattern"]
        while (
            alarm_on
            and recurring_pattern
            and alarm < dt.now()
            and RECURRING_PATTERN_ISO_SET[recurring_pattern]
            and alarm.isoweekday not in RECURRING_PATTERN_ISO_SET[recurring_pattern]
        ):
            alarm += datetime.timedelta(days=1)
        if alarm != value[1][self._sensor_property]:
            _LOGGER.debug(
                "Alarm with recurrence %s set to %s",
                RECURRING_PATTERN[recurring_pattern],
                alarm,
            )
            value[1][self._sensor_property] = alarm
        return value