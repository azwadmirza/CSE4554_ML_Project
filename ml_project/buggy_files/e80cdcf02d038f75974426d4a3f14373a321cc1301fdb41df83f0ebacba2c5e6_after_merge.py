def sync_list_repositories(executable_path, python_file, module_name, working_directory, attribute):
    from dagster.grpc.types import ListRepositoriesResponse, ListRepositoriesInput

    result = check.inst(
        execute_unary_api_cli_command(
            executable_path,
            'list_repositories',
            ListRepositoriesInput(
                module_name=module_name,
                python_file=python_file,
                working_directory=working_directory,
                attribute=attribute,
            ),
        ),
        (ListRepositoriesResponse, SerializableErrorInfo),
    )
    if isinstance(result, SerializableErrorInfo):
        raise DagsterUserCodeProcessError(
            result.to_string(), user_code_process_error_infos=[result]
        )
    else:
        return result