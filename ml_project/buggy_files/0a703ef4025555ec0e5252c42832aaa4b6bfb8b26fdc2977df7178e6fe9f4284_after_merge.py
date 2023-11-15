def execution_context_labels(config_details, environment_file):
    extra_labels = [
        '{0}={1}'.format(LABEL_WORKING_DIR, os.path.abspath(config_details.working_dir))
    ]

    if not use_config_from_stdin(config_details):
        extra_labels.append('{0}={1}'.format(LABEL_CONFIG_FILES, config_files_label(config_details)))

    if environment_file is not None:
        extra_labels.append('{0}={1}'.format(LABEL_ENVIRONMENT_FILE,
                                             os.path.normpath(environment_file)))
    return extra_labels