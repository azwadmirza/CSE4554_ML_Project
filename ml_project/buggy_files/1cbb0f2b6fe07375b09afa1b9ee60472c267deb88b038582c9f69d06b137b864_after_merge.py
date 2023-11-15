    def night_mode(self, night_mode):
        """Switch on/off the speaker's night mode.

        :param night_mode: Enable or disable night mode
        :type night_mode: bool
        :raises NotSupportedException: If the device does not support
        night mode.
        """
        if not self.is_soundbar:
            message = 'This device does not support night mode'
            raise NotSupportedException(message)

        self.renderingControl.SetEQ([
            ('InstanceID', 0),
            ('EQType', 'NightMode'),
            ('DesiredValue', int(night_mode))
        ])