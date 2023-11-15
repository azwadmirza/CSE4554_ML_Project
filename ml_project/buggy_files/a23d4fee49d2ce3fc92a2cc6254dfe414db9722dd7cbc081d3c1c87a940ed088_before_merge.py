def config_files_label(config_details):
    return ",".join(
        map(str, (os.path.normpath(c.filename) for c in config_details.config_files)))