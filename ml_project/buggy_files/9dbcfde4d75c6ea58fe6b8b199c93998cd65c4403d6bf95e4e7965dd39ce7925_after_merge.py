    def _update_recurring_alarm(self, value):
        _LOGGER.debug("Sensor value %s", value)
        alarm = value[1][self._sensor_property]
        reminder = None
        if isinstance(value[1][self._sensor_property], int):
            reminder = True
            alarm = dt.as_local(
                self._round_time(
                    datetime.datetime.fromtimestamp(alarm / 1000, tz=LOCAL_TIMEZONE)
                )
            )
        alarm_on = value[1]["status"] == "ON"
        recurring_pattern = value[1].get("recurringPattern")
        while (
            alarm_on
            and recurring_pattern
            and RECURRING_PATTERN_ISO_SET[recurring_pattern]
            and alarm.isoweekday not in RECURRING_PATTERN_ISO_SET[recurring_pattern]
            and alarm < dt.now()
        ):
            alarm += datetime.timedelta(days=1)
        if reminder:
            alarm = dt.as_timestamp(alarm) * 1000
        if alarm != value[1][self._sensor_property]:
            _LOGGER.debug(
                "%s with recurrence %s set to %s",
                value[1]["type"],
                RECURRING_PATTERN[recurring_pattern],
                alarm,
            )
            value[1][self._sensor_property] = alarm
        return value