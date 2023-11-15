def config_files_label(config_details):
    return ",".join(
        map(str, (config_file_path(c.filename) for c in config_details.config_files)))