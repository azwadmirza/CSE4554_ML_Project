def write(settings_path, settings_data, merge=True):
    """Write data to a settings file.

    :param settings_path: the filepath
    :param settings_data: a dictionary with data
    :param merge: boolean if existing file should be merged with new data
    """
    if settings_path.exists() and merge:  # pragma: no cover
        object_merge(
            ConfigObj(
                io.open(
                    str(settings_path),
                    encoding=default_settings.ENCODING_FOR_DYNACONF
                )
            ).dict(),
            settings_data
        )
    new = ConfigObj()
    new.update(settings_data)
    new.write(open(str(settings_path), 'bw'))