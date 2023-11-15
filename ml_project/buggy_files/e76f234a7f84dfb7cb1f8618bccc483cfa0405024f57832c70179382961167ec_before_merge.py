def get_area_file():
    conf, successes = get_config("satpy.cfg")
    if conf is None or not successes:
        LOG.warning(
            "Couldn't find the satpy.cfg file. Do you have one ? is it in $PPP_CONFIG_DIR ?")
        return None

    try:
        fn = os.path.join(conf.get("projector", "area_directory") or "",
                          conf.get("projector", "area_file"))
        return get_config_path(fn)
    except configparser.NoSectionError:
        LOG.warning("Couldn't find 'projector' section of 'satpy.cfg'")