def write(settings_path, settings_data, merge=True):
    """Write data to a settings file.

    :param settings_path: the filepath
    :param settings_data: a dictionary with data
    :param merge: boolean if existing file should be merged with new data
    """
    settings_path = Path(settings_path)
    if settings_path.exists() and merge:  # pragma: no cover
        existing = DynaconfDict()
        load(existing, str(settings_path))
        object_merge(
            existing,
            settings_data
        )
    with io.open(
        str(settings_path), 'w',
        encoding=default_settings.ENCODING_FOR_DYNACONF
    ) as f:
        f.writelines(
            ["{} = {}\n".format(k.upper(), repr(v))
             for k, v in settings_data.items()]
        )