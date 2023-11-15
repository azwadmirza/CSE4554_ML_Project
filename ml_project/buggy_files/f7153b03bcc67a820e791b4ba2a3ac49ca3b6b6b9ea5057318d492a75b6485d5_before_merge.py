    def get_last_device_serial(self):
        """Identify the last device's serial number."""
        try:
            response = self._get_request('/api/activities?startTime=&size=1&offset=1')
            last_activity = response.json()['activities'][0]
        except Exception as ex:
            template = ("An exception of type {0} occurred."
                        " Arguments:\n{1!r}")
            message = template.format(type(ex).__name__, ex.args)
            _LOGGER.debug("An error occured accessing the API: {}".format(message))
            return None

        # Ignore discarded activity records
        if last_activity['activityStatus'](0) != 'DISCARDED_NON_DEVICE_DIRECTED_INTENT':
            return last_activity['sourceDeviceIds'][0]['serialNumber']
        else:
            return None