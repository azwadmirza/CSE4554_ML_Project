    def _fix_alarm_date_time(self, value):
        import pytz

        if self._sensor_property != "date_time" or not value:
            return value
        naive_time = dt.parse_datetime(value[1][self._sensor_property])
        timezone = pytz.timezone(self._client._timezone)
        if timezone and naive_time:
            value[1][self._sensor_property] = timezone.localize(naive_time)
        else:
            _LOGGER.warning(
                "%s is returning erroneous data."
                "Returned times may be wrong. "
                "Please confirm the timezone in the Alexa app is correct. "
                "Debugging info: \nRaw: %s \nNaive Time: %s "
                "\nTimezone: %s",
                self._client.name,
                value[1],
                naive_time,
                self._client._timezone,
            )
        return value