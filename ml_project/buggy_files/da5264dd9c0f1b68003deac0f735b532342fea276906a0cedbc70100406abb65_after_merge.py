def process_service(service_config):
    working_dir = service_config.working_dir
    service_dict = dict(service_config.config)

    if 'env_file' in service_dict:
        service_dict['env_file'] = [
            expand_path(working_dir, path)
            for path in to_list(service_dict['env_file'])
        ]

    if 'build' in service_dict:
        process_build_section(service_dict, working_dir)

    if 'volumes' in service_dict and service_dict.get('volume_driver') is None:
        service_dict['volumes'] = resolve_volume_paths(working_dir, service_dict)

    if 'sysctls' in service_dict:
        service_dict['sysctls'] = build_string_dict(parse_sysctls(service_dict['sysctls']))

    if 'labels' in service_dict:
        service_dict['labels'] = parse_labels(service_dict['labels'])

    service_dict = process_depends_on(service_dict)

    for field in ['dns', 'dns_search', 'tmpfs']:
        if field in service_dict:
            service_dict[field] = to_list(service_dict[field])

    service_dict = process_blkio_config(process_ports(
        process_healthcheck(service_dict)
    ))

    return service_dict