def configs_for_reader(reader=None, ppp_config_dir=None):
    """Generate reader configuration files for one or more readers.

    Args:
        reader (Optional[str]): Yield configs only for this reader
        ppp_config_dir (Optional[str]): Additional configuration directory
            to search for reader configuration files.

    Returns: Generator of lists of configuration files

    """
    search_paths = (ppp_config_dir,) if ppp_config_dir else tuple()
    if reader is not None:
        if not isinstance(reader, (list, tuple)):
            reader = [reader]
        # check for old reader names
        new_readers = []
        for reader_name in reader:
            if reader_name.endswith('.yaml') or reader_name not in OLD_READER_NAMES:
                new_readers.append(reader_name)
                continue

            new_name = OLD_READER_NAMES[reader_name]
            # Satpy 0.11 only displays a warning
            # Satpy 0.13 will raise an exception
            raise ValueError("Reader name '{}' has been deprecated, use '{}' instead.".format(reader_name, new_name))
            # Satpy 0.15 or 1.0, remove exception and mapping

        reader = new_readers
        # given a config filename or reader name
        config_files = [r if r.endswith('.yaml') else r + '.yaml' for r in reader]
    else:
        reader_configs = glob_config(os.path.join('readers', '*.yaml'),
                                     *search_paths)
        config_files = set(reader_configs)

    for config_file in config_files:
        config_basename = os.path.basename(config_file)
        reader_name = os.path.splitext(config_basename)[0]
        reader_configs = config_search_paths(
            os.path.join("readers", config_basename), *search_paths)

        if not reader_configs:
            # either the reader they asked for does not exist
            # or satpy is improperly configured and can't find its own readers
            raise ValueError("No reader named: {}".format(reader_name))

        yield reader_configs