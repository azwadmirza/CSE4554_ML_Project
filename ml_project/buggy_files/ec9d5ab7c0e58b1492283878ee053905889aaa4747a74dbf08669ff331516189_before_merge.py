    def get_config(self, source='running', flags=None, format=None):
        """Retrieves the specified configuration from the device

        This method will retrieve the configuration specified by source and
        return it to the caller as a string.  Subsequent calls to this method
        will retrieve a new configuration from the device

        :param source: The configuration source to return from the device.
            This argument accepts either `running` or `startup` as valid values.

        :param flag: For devices that support configuration filtering, this
            keyword argument is used to filter the returned configuration.
            The use of this keyword argument is device dependent adn will be
            silently ignored on devices that do not support it.

        :param format: For devices that support fetching different configuration
            format, this keyword argument is used to specify the format in which
            configuration is to be retrieved.

        :return: The device configuration as specified by the source argument.
        """
        pass