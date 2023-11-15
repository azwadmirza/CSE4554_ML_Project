        def get_filename(config_name):
            filename, ext = os.path.splitext(config_name)
            if ext not in (".yaml", ".yml"):
                config_name = "{}{}".format(config_name, ".yaml")
            return config_name