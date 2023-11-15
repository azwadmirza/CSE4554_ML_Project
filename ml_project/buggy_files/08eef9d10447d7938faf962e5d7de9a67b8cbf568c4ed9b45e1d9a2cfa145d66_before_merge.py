def finalize_service(service_config, service_names, version, environment):
    service_dict = dict(service_config.config)

    if 'environment' in service_dict or 'env_file' in service_dict:
        service_dict['environment'] = resolve_environment(service_dict, environment)
        service_dict.pop('env_file', None)

    if 'volumes_from' in service_dict:
        service_dict['volumes_from'] = [
            VolumeFromSpec.parse(vf, service_names, version)
            for vf in service_dict['volumes_from']
        ]

    if 'volumes' in service_dict:
        service_dict['volumes'] = [
            VolumeSpec.parse(
                v, environment.get_boolean('COMPOSE_CONVERT_WINDOWS_PATHS')
            ) for v in service_dict['volumes']
        ]

    if 'net' in service_dict:
        network_mode = service_dict.pop('net')
        container_name = get_container_name_from_network_mode(network_mode)
        if container_name and container_name in service_names:
            service_dict['network_mode'] = 'service:{}'.format(container_name)
        else:
            service_dict['network_mode'] = network_mode

    if 'networks' in service_dict:
        service_dict['networks'] = parse_networks(service_dict['networks'])

    if 'restart' in service_dict:
        service_dict['restart'] = parse_restart_spec(service_dict['restart'])

    normalize_build(service_dict, service_config.working_dir, environment)

    service_dict['name'] = service_config.name
    return normalize_v1_service_format(service_dict)