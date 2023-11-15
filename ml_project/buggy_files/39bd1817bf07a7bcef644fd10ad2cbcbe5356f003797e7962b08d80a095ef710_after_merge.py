def handle_missing_index_file(app, tool_path, sample_files, repository_tools_tups, sample_files_copied):
    """
    Inspect each tool to see if it has any input parameters that are dynamically
    generated select lists that depend on a .loc file.  This method is not called
    from the tool shed, but from Galaxy when a repository is being installed.
    """
    for index, repository_tools_tup in enumerate(repository_tools_tups):
        tup_path, guid, repository_tool = repository_tools_tup
        params_with_missing_index_file = repository_tool.params_with_missing_index_file
        for param in params_with_missing_index_file:
            options = param.options
            missing_file_name = basic_util.strip_path(options.missing_index_file)
            if missing_file_name not in sample_files_copied:
                # The repository must contain the required xxx.loc.sample file.
                for sample_file in sample_files:
                    sample_file_name = basic_util.strip_path(sample_file)
                    if sample_file_name == '%s.sample' % missing_file_name:
                        target_path = copy_sample_file(app, os.path.join(tool_path, sample_file))
                        if options.tool_data_table and options.tool_data_table.missing_index_file:
                            options.tool_data_table.handle_found_index_file(target_path)
                        sample_files_copied.append(target_path)
                        break
    return repository_tools_tups, sample_files_copied