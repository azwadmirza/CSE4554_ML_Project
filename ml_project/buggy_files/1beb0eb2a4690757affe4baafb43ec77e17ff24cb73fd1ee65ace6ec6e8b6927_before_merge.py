def get_config_path_from_options(base_dir, options, environment):
    file_option = options.get('--file')
    if file_option:
        return file_option

    config_files = environment.get('COMPOSE_FILE')
    if config_files:
        pathsep = environment.get('COMPOSE_PATH_SEPARATOR', os.pathsep)
        return config_files.split(pathsep)
    return None