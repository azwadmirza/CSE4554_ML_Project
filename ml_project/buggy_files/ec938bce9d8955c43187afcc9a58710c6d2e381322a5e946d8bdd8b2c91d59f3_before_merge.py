def list_repositories_command(args):
    check.inst_param(args, 'args', ListRepositoriesInput)
    python_file, module_name, working_directory, attribute = (
        args.python_file,
        args.module_name,
        args.working_directory,
        args.attribute,
    )
    loadable_targets = get_loadable_targets(python_file, module_name, working_directory, attribute)
    return ListRepositoriesResponse(
        [
            LoadableRepositorySymbol(
                attribute=lt.attribute,
                repository_name=repository_def_from_target_def(lt.target_definition).name,
            )
            for lt in loadable_targets
        ]
    )