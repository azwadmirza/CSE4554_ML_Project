    def _fix_alarm_date_time(self, value):
        import pytz

        if self._sensor_property != "date_time" or not value:
            return value
        naive_time = dt.parse_datetime(value[1][self._sensor_property])
        timezone = pytz.timezone(self._client._timezone)
        if timezone:
            value[1][self._sensor_property] = timezone.localize(naive_time)
        else:
            _LOGGER.warning(
                "%s does not have a timezone set. "
                "Returned times may be wrong. "
                "Please set the timezone in the Alexa app.",
                self._client.name,
            )
        return value