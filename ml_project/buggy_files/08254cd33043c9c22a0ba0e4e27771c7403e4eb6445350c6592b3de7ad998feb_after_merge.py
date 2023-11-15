    def set(self, key, value):
        """ Store setting, but adding isn't allowed. All possible settings must be in default settings file. """
        key = key.lower()

        # Load user setting's values (for easy merging)
        user_values = {}
        for item in self._data:
            if "setting" in item and "value" in item:
                user_values[item["setting"].lower()] = item

        # Save setting
        if key in user_values:
            user_values[key]["value"] = value
        else:
            log.warn(
                "{} key '{}' not valid. The following are valid: {}".format(
                self.data_type, key,
                list(self._data.keys()),
                ))