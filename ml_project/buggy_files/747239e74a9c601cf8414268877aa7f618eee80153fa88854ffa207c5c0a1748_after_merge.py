def autoupdate(runner):
    """Auto-update the pre-commit config to the latest versions of repos."""
    retv = 0
    output_configs = []
    changed = False

    input_configs = load_config(
        runner.config_file_path,
        load_strategy=ordered_load,
    )

    for repo_config in input_configs:
        if is_local_hooks(repo_config):
            continue
        sys.stdout.write('Updating {0}...'.format(repo_config['repo']))
        sys.stdout.flush()
        try:
            new_repo_config = _update_repository(repo_config, runner)
        except RepositoryCannotBeUpdatedError as error:
            print(error.args[0])
            output_configs.append(repo_config)
            retv = 1
            continue

        if new_repo_config['sha'] != repo_config['sha']:
            changed = True
            print(
                'updating {0} -> {1}.'.format(
                    repo_config['sha'], new_repo_config['sha'],
                )
            )
            output_configs.append(new_repo_config)
        else:
            print('already up to date.')
            output_configs.append(repo_config)

    if changed:
        with open(runner.config_file_path, 'w') as config_file:
            config_file.write(
                ordered_dump(
                    remove_defaults(output_configs, CONFIG_JSON_SCHEMA),
                    **C.YAML_DUMP_KWARGS
                )
            )

    return retv