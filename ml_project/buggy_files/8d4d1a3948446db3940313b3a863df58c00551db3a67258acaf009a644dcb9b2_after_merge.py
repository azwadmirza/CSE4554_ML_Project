def set_config(context, config_file):
    full_path = os.path.join("features/configs", config_file)

    context.config_path = os.path.abspath(full_path)

    if config_file.endswith("yaml") and os.path.exists(full_path):
        # Add jrnl version to file for 2.x journals
        with open(context.config_path, "a") as cf:
            cf.write("version: {}".format(__version__))