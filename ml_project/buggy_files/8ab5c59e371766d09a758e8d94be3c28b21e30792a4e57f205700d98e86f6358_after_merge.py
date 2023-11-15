def write(settings_path, settings_data, merge=True):
    """Write data to a settings file.

    :param settings_path: the filepath
    :param settings_data: a dictionary with data
    :param merge: boolean if existing file should be merged with new data
    """
    settings_path = Path(settings_path)
    if settings_path.exists() and merge:  # pragma: no cover
        object_merge(
            json.load(
                io.open(
                    str(settings_path),
                    encoding=default_settings.ENCODING_FOR_DYNACONF
                )
            ),
            settings_data
        )

    json.dump(
        settings_data,
        io.open(
            str(settings_path), 'w',
            encoding=default_settings.ENCODING_FOR_DYNACONF
        )
    )