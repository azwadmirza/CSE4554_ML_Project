def set_config(context, config_file):
    full_path = os.path.join("features/configs", config_file)

    install.CONFIG_FILE_PATH = os.path.abspath(full_path)
    if config_file.endswith("yaml") and os.path.exists(full_path):
        # Add jrnl version to file for 2.x journals
        with open(install.CONFIG_FILE_PATH, "a") as cf:
            cf.write("version: {}".format(__version__))