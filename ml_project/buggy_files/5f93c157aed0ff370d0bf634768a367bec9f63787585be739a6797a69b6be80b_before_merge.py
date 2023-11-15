        def get_filename(config_name):
            filename, ext = os.path.splitext(config_name)
            if ext == "":
                ext = ".yaml"
            return "{}{}".format(filename, ext)