def _get_command_to_run(query):
    params = shlex_split(query)
    __check_query_params(params)

    cmd = []
    for c in command:
        if c == '{{QUERY}}':
            cmd.extend(params)
        else:
            cmd.append(c)

    return cmd