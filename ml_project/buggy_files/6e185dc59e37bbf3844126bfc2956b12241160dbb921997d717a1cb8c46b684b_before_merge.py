    def get_config(self, instance):
        instance_id = hash_mutable(instance)
        config = self.config.get(instance_id)
        if config is None:
            config = {}

            try:
                api_url = instance['api_url']
                api_version = api_url[-1]
                if api_version not in self.api_versions:
                    self.log.warning(
                        'Unknown Vault API version `{}`, using version '
                        '`{}`'.format(api_version, self.DEFAULT_API_VERSION)
                    )

                config['api_url'] = api_url
                config['api'] = self.api_versions.get(api_version, self.DEFAULT_API_VERSION)['functions']
            except KeyError:
                self.log.error('Vault configuration setting `api_url` is required')
                return

            client_token = instance.get('client_token')
            config['headers'] = {'X-Vault-Token': client_token} if client_token else None

            username = instance.get('username')
            password = instance.get('password')
            config['auth'] = (username, password) if username and password else None

            ssl_cert = instance.get('ssl_cert')
            ssl_private_key = instance.get('ssl_private_key')
            if isinstance(ssl_cert, string_types):
                if isinstance(ssl_private_key, string_types):
                    config['ssl_cert'] = (ssl_cert, ssl_private_key)
                else:
                    config['ssl_cert'] = ssl_cert
            else:
                config['ssl_cert'] = None

            if isinstance(instance.get('ssl_ca_cert'), string_types):
                config['ssl_verify'] = instance['ssl_ca_cert']
            else:
                config['ssl_verify'] = is_affirmative(instance.get('ssl_verify', True))

            config['ssl_ignore_warning'] = is_affirmative(instance.get('ssl_ignore_warning', False))
            config['proxies'] = self.get_instance_proxy(instance, config['api_url'])
            config['timeout'] = int(instance.get('timeout', 20))
            config['tags'] = instance.get('tags', [])

            # Keep track of the previous cluster leader to detect changes.
            config['leader'] = None
            config['detect_leader'] = is_affirmative(instance.get('detect_leader'))

            self.config[instance_id] = config

        return config