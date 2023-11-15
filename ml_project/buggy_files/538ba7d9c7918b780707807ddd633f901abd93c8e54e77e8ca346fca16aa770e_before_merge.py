    def version(self):
        if 'version' not in self.config:
            return V1

        version = self.config['version']

        if isinstance(version, dict):
            log.warning('Unexpected type for "version" key in "{}". Assuming '
                        '"version" is the name of a service, and defaulting to '
                        'Compose file version 1.'.format(self.filename))
            return V1

        if not isinstance(version, six.string_types):
            raise ConfigurationError(
                'Version in "{}" is invalid - it should be a string.'
                .format(self.filename))

        if version == '1':
            raise ConfigurationError(
                'Version in "{}" is invalid. {}'
                .format(self.filename, VERSION_EXPLANATION)
            )

        if version == '2':
            return const.COMPOSEFILE_V2_0

        if version == '3':
            return const.COMPOSEFILE_V3_0

        return ComposeVersion(version)