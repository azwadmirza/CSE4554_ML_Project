    def _get_conn(self, instance):
        no_cache = is_affirmative(instance.get('disable_connection_cache', False))
        key = self._generate_instance_key(instance)

        if no_cache or key not in self.connections:
            try:
                # Only send useful parameters to the redis client constructor
                list_params = [
                    'host', 'port', 'db', 'password', 'socket_timeout',
                    'connection_pool', 'charset', 'errors', 'unix_socket_path', 'ssl',
                    'ssl_certfile', 'ssl_keyfile', 'ssl_ca_certs', 'ssl_cert_reqs'
                ]

                # Set a default timeout (in seconds) if no timeout is specified in the instance config
                instance['socket_timeout'] = instance.get('socket_timeout', 5)
                connection_params = dict((k, instance[k]) for k in list_params if k in instance)
                # If caching is disabled, we overwrite the dictionary value so the old connection
                # will be closed as soon as the corresponding Python object gets garbage collected
                self.connections[key] = redis.Redis(**connection_params)

            except TypeError:
                msg = "You need a redis library that supports authenticated connections. Try sudo easy_install redis."
                raise Exception(msg)

        return self.connections[key]