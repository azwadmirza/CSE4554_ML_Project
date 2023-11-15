    def from_config(cls, name, config_data, client):
        """
        Construct a Project from a config.Config object.
        """
        use_networking = (config_data.version and config_data.version != V1)
        networks = build_networks(name, config_data, client)
        project_networks = ProjectNetworks.from_services(
            config_data.services,
            networks,
            use_networking)
        volumes = ProjectVolumes.from_config(name, config_data, client)
        project = cls(name, [], client, project_networks, volumes, config_data.version)

        for service_dict in config_data.services:
            service_dict = dict(service_dict)
            if use_networking:
                service_networks = get_networks(service_dict, networks)
            else:
                service_networks = {}

            service_dict.pop('networks', None)
            links = project.get_links(service_dict)
            network_mode = project.get_network_mode(
                service_dict, list(service_networks.keys())
            )
            pid_mode = project.get_pid_mode(service_dict)
            volumes_from = get_volumes_from(project, service_dict)

            if config_data.version != V1:
                service_dict['volumes'] = [
                    volumes.namespace_spec(volume_spec)
                    for volume_spec in service_dict.get('volumes', [])
                ]

            secrets = get_secrets(
                service_dict['name'],
                service_dict.pop('secrets', None) or [],
                config_data.secrets)

            project.services.append(
                Service(
                    service_dict.pop('name'),
                    client=client,
                    project=name,
                    use_networking=use_networking,
                    networks=service_networks,
                    links=links,
                    network_mode=network_mode,
                    volumes_from=volumes_from,
                    secrets=secrets,
                    pid_mode=pid_mode,
                    **service_dict)
            )

        return project