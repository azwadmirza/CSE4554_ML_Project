def load(config_details):
    """Load the configuration from a working directory and a list of
    configuration files.  Files are loaded in order, and merged on top
    of each other to create the final configuration.

    Return a fully interpolated, extended and validated configuration.
    """

    def build_service(filename, service_name, service_dict):
        loader = ServiceLoader(
            config_details.working_dir,
            filename,
            service_name,
            service_dict)
        service_dict = loader.make_service_dict()
        validate_paths(service_dict)
        return service_dict

    def load_file(filename, config):
        processed_config = pre_process_config(config)
        validate_against_fields_schema(processed_config)
        return [
            build_service(filename, name, service_config)
            for name, service_config in processed_config.items()
        ]

    def merge_services(base, override):
        all_service_names = set(base) | set(override)
        return {
            name: merge_service_dicts(base.get(name, {}), override.get(name, {}))
            for name in all_service_names
        }

    config_file = config_details.config_files[0]
    for next_file in config_details.config_files[1:]:
        config_file = ConfigFile(
            config_file.filename,
            merge_services(config_file.config, next_file.config))

    return load_file(config_file.filename, config_file.config)