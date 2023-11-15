def process_service(service_config):
    working_dir = service_config.working_dir
    service_dict = dict(service_config.config)

    if 'env_file' in service_dict:
        service_dict['env_file'] = [
            expand_path(working_dir, path)
            for path in to_list(service_dict['env_file'])
        ]

    if 'build' in service_dict:
        if isinstance(service_dict['build'], six.string_types):
            service_dict['build'] = resolve_build_path(working_dir, service_dict['build'])
        elif isinstance(service_dict['build'], dict):
            if 'context' in service_dict['build']:
                path = service_dict['build']['context']
                service_dict['build']['context'] = resolve_build_path(working_dir, path)
            if 'labels' in service_dict['build']:
                service_dict['build']['labels'] = parse_labels(service_dict['build']['labels'])

    if 'volumes' in service_dict and service_dict.get('volume_driver') is None:
        service_dict['volumes'] = resolve_volume_paths(working_dir, service_dict)

    if 'sysctls' in service_dict:
        service_dict['sysctls'] = build_string_dict(parse_sysctls(service_dict['sysctls']))

    service_dict = process_depends_on(service_dict)

    for field in ['dns', 'dns_search', 'tmpfs']:
        if field in service_dict:
            service_dict[field] = to_list(service_dict[field])

    service_dict = process_blkio_config(process_ports(
        process_healthcheck(service_dict)
    ))

    return service_dict