    def _load_baseline_from_dict(cls, data):
        """Initializes a SecretsCollection object from dictionary.

        :type data: dict
        :param data: properly formatted dictionary to load SecretsCollection from.

        :rtype: SecretsCollection
        :raises: IOError
        """
        result = SecretsCollection()
        if not all(key in data for key in (
            'exclude_regex',
            'plugins_used',
            'results',
            'version',
        )):
            raise IOError

        result.exclude_regex = data['exclude_regex']

        plugins = []
        for plugin in data['plugins_used']:
            plugin_classname = plugin.pop('name')
            plugins.append(initialize.from_plugin_classname(
                plugin_classname,
                **plugin
            ))
        result.plugins = tuple(plugins)

        for filename in data['results']:
            result.data[filename] = {}

            for item in data['results'][filename]:
                secret = PotentialSecret(
                    item['type'],
                    filename,
                    item['line_number'],
                    'will be replaced',
                )
                secret.secret_hash = item['hashed_secret']
                result.data[filename][secret] = secret

        result.version = data['version']

        return result