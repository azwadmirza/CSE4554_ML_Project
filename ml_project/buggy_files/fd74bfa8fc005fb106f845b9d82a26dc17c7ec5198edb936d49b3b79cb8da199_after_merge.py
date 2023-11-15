def migrate_config(config_file: str, quiet: bool = False) -> int:
    # ensure that the configuration is a valid pre-commit configuration
    load_config(config_file)

    with open(config_file) as f:
        orig_contents = contents = f.read()

    contents = _migrate_map(contents)
    contents = _migrate_sha_to_rev(contents)

    if contents != orig_contents:
        with open(config_file, 'w') as f:
            f.write(contents)

        print('Configuration has been migrated.')
    elif not quiet:
        print('Configuration is already migrated.')
    return 0