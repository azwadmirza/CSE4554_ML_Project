    def _get_container_create_options(
            self,
            override_options,
            number,
            one_off=False,
            previous_container=None):
        add_config_hash = (not one_off and not override_options)

        container_options = dict(
            (k, self.options[k])
            for k in DOCKER_CONFIG_KEYS if k in self.options)
        override_volumes = override_options.pop('volumes', [])
        container_options.update(override_options)

        if not container_options.get('name'):
            container_options['name'] = self.get_container_name(self.name, number, one_off)

        container_options.setdefault('detach', True)

        # If a qualified hostname was given, split it into an
        # unqualified hostname and a domainname unless domainname
        # was also given explicitly. This matches behavior
        # until Docker Engine 1.11.0 - Docker API 1.23.
        if (version_lt(self.client.api_version, '1.23') and
                'hostname' in container_options and
                'domainname' not in container_options and
                '.' in container_options['hostname']):
            parts = container_options['hostname'].partition('.')
            container_options['hostname'] = parts[0]
            container_options['domainname'] = parts[2]

        if (version_gte(self.client.api_version, '1.25') and
                'stop_grace_period' in self.options):
            container_options['stop_timeout'] = self.stop_timeout(None)

        if 'ports' in container_options or 'expose' in self.options:
            container_options['ports'] = build_container_ports(
                formatted_ports(container_options.get('ports', [])),
                self.options)

        if 'volumes' in container_options or override_volumes:
            container_options['volumes'] = list(set(
                container_options.get('volumes', []) + override_volumes
            ))

        container_options['environment'] = merge_environment(
            self.options.get('environment'),
            override_options.get('environment'))

        container_options['labels'] = merge_labels(
            self.options.get('labels'),
            override_options.get('labels'))

        container_volumes = []
        container_mounts = []
        if 'volumes' in container_options:
            container_volumes = [
                v for v in container_options.get('volumes') if isinstance(v, VolumeSpec)
            ]
            container_mounts = [v for v in container_options.get('volumes') if isinstance(v, MountSpec)]

        binds, affinity = merge_volume_bindings(
            container_volumes, self.options.get('tmpfs') or [], previous_container,
            container_mounts
        )
        override_options['binds'] = binds
        container_options['environment'].update(affinity)

        container_options['volumes'] = dict((v.internal, {}) for v in container_volumes or {})
        override_options['mounts'] = [build_mount(v) for v in container_mounts] or None

        secret_volumes = self.get_secret_volumes()
        if secret_volumes:
            if version_lt(self.client.api_version, '1.30'):
                override_options['binds'].extend(v.legacy_repr() for v in secret_volumes)
                container_options['volumes'].update(
                    (v.target, {}) for v in secret_volumes
                )
            else:
                override_options['mounts'] = override_options.get('mounts') or []
                override_options['mounts'].extend([build_mount(v) for v in secret_volumes])

        container_options['image'] = self.image_name

        container_options['labels'] = build_container_labels(
            container_options.get('labels', {}),
            self.labels(one_off=one_off),
            number,
            self.config_hash if add_config_hash else None)

        # Delete options which are only used in HostConfig
        for key in HOST_CONFIG_KEYS:
            container_options.pop(key, None)

        container_options['host_config'] = self._get_container_host_config(
            override_options,
            one_off=one_off)

        networking_config = self.build_default_networking_config()
        if networking_config:
            container_options['networking_config'] = networking_config

        container_options['environment'] = format_environment(
            container_options['environment'])
        return container_options